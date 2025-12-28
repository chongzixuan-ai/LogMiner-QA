Feature: Journey ABC123
  Scenario: Validate journey ABC123
  Given a sanitized transaction journey
  When the system observes login_event
  Then the compliance checks pass

Feature: Journey b7be4140a8b257293f257e4f425b8965b50ed83eabb8cee4968aa811ba12a42e
  Scenario: Validate journey b7be4140a8b257293f257e4f425b8965b50ed83eabb8cee4968aa811ba12a42e
  Given a sanitized transaction journey
  When the system observes transaction_event
  When the system observes error_event
  Then the compliance checks pass

Feature: Journey 086bbbba794a81fd9b082645257255b43d0dc54e89fc3d77c2d54e721ba1bcdc
  Scenario: Validate journey 086bbbba794a81fd9b082645257255b43d0dc54e89fc3d77c2d54e721ba1bcdc
  Given a sanitized transaction journey
  When the system observes generic_event
  Then the compliance checks pass