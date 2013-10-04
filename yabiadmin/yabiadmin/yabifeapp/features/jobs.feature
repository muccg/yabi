Feature: User can see jobs they've run.
Scenario: User views jobs they're run
    Given I go to "/"
    When I log in as "demo" with "demo" password
    When I click "jobs"
    Then I should see "click the design tab to design a new workflow"