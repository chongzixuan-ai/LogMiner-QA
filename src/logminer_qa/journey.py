"""
User journey modeling using sequence-based representations.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, Iterable, List, Sequence, Tuple

if TYPE_CHECKING:  # pragma: no cover
    from tensorflow import keras

import numpy as np
from sklearn.preprocessing import LabelEncoder

LOGGER = logging.getLogger(__name__)


MAX_SEQUENCE_LENGTH = 50


@dataclass(slots=True)
class JourneyModelConfig:
    embedding_dim: int = 64
    lstm_units: int = 128
    dense_units: int = 64
    dropout_rate: float = 0.3
    learning_rate: float = 1e-3
    epochs: int = 5
    batch_size: int = 32
    min_sequences: int = 50
    max_sequence_length: int = MAX_SEQUENCE_LENGTH


@dataclass(slots=True)
class JourneyInsights:
    anomalous_sequences: List[Dict[str, object]] = field(default_factory=list)
    next_event_probabilities: Dict[str, Dict[str, float]] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, object]:
        return {
            "anomalous_sequences": self.anomalous_sequences,
            "next_event_probabilities": self.next_event_probabilities,
        }


@dataclass(slots=True)
class JourneyAnalyzer:
    config: JourneyModelConfig = field(default_factory=JourneyModelConfig)
    label_encoder: LabelEncoder = field(default_factory=LabelEncoder, init=False)
    model: "keras.Model | None" = field(default=None, init=False)
    trained: bool = field(default=False, init=False)

    def fit(self, journeys: Dict[str, Sequence[str]]) -> None:
        keras = self._lazy_import_keras()
        if keras is None:
            self.trained = False
            return

        sequences = [list(events)[: self.config.max_sequence_length] for events in journeys.values() if events]
        sequences = [seq for seq in sequences if len(seq) >= 2]
        if len(sequences) < self.config.min_sequences:
            LOGGER.info(
                "Skipping journey model training: only %d sequences (requires %d).",
                len(sequences),
                self.config.min_sequences,
            )
            self.trained = False
            return

        unique_events = sorted({event for seq in sequences for event in seq})
        if len(unique_events) < 2:
            LOGGER.info("Skipping journey model training: not enough unique events.")
            self.trained = False
            return

        self.label_encoder.fit(unique_events)
        encoded_sequences = [self.label_encoder.transform(seq) for seq in sequences]
        num_events = len(self.label_encoder.classes_)
        padding_token = num_events
        padded_sequences = keras.utils.pad_sequences(
            encoded_sequences,
            maxlen=self.config.max_sequence_length,
            padding="post",
            truncating="post",
            value=padding_token,
        )
        X, y = self._build_training_pairs(padded_sequences, padding_token, num_events)
        if X.size == 0 or y.size == 0:
            LOGGER.info("Skipping journey model training: insufficient data after padding.")
            self.trained = False
            return

        self.model = self._build_model(num_events=num_events + 1)
        self.model.fit(
            X,
            y,
            epochs=self.config.epochs,
            batch_size=self.config.batch_size,
            verbose=0,
        )
        self.trained = True

    def analyze(self, journeys: Dict[str, Sequence[str]]) -> JourneyInsights:
        keras = self._lazy_import_keras()
        insights = JourneyInsights()
        if keras is None or not self.trained or not self.model:
            return insights

        num_events = len(self.label_encoder.classes_)
        padding_token = num_events
        for journey_id, events in journeys.items():
            if not events:
                continue
            known_events = [event for event in events if event in self.label_encoder.classes_]
            if not known_events:
                continue
            encoded = self.label_encoder.transform(known_events)
            if encoded.size == 0:
                continue
            padded = keras.utils.pad_sequences(
                [encoded],
                maxlen=self.config.max_sequence_length - 1,
                padding="post",
                truncating="post",
                value=padding_token,
            )
            predictions = self.model.predict(padded, verbose=0)[0]
            predicted_index = int(np.argmax(predictions))
            if predicted_index >= num_events:
                continue
            predicted_event = self.label_encoder.inverse_transform([predicted_index])[0]
            actual_next = known_events[-1]
            confidence = float(np.max(predictions))
            if predicted_event != actual_next and confidence > 0.6:
                insights.anomalous_sequences.append(
                    {
                        "journey_id": journey_id,
                        "predicted_next": predicted_event,
                        "actual_last": actual_next,
                        "confidence": confidence,
                    }
                )
            insights.next_event_probabilities[journey_id] = {
                event: float(prob)
                for event, prob in zip(self.label_encoder.classes_, predictions[:num_events])
            }
        return insights

    def _build_training_pairs(
        self, sequences: np.ndarray, padding_token: int, num_events: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        keras = self._lazy_import_keras()
        if keras is None:
            return np.asarray([]), np.asarray([])
        X = sequences[:, :-1]
        y_indices = sequences[:, -1]
        mask = y_indices != padding_token
        X = X[mask]
        y_indices = y_indices[mask]
        if y_indices.size == 0:
            return np.asarray([]), np.asarray([])
        y = keras.utils.to_categorical(y_indices, num_classes=num_events + 1)
        return X, y[:, :num_events]

    def _build_model(self, num_events: int) -> keras.Model:
        keras = self._lazy_import_keras()
        if keras is None:
            raise RuntimeError("TensorFlow/Keras not available.")
        inputs = keras.Input(shape=(self.config.max_sequence_length - 1,))
        x = keras.layers.Embedding(num_events, self.config.embedding_dim, mask_zero=True)(inputs)
        x = keras.layers.LSTM(self.config.lstm_units)(x)
        x = keras.layers.Dropout(self.config.dropout_rate)(x)
        x = keras.layers.Dense(self.config.dense_units, activation="relu")(x)
        outputs = keras.layers.Dense(num_events - 1, activation="softmax")(x)
        model = keras.Model(inputs, outputs)
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=self.config.learning_rate),
            loss="categorical_crossentropy",
            metrics=["accuracy"],
        )
        return model

    @staticmethod
    def _lazy_import_keras():
        try:
            from tensorflow import keras  # type: ignore
        except Exception as exc:  # pragma: no cover
            LOGGER.warning("TensorFlow/Keras unavailable: %s", exc)
            return None
        return keras

