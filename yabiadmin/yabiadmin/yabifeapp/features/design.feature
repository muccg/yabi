Feature: User can design a workflow
Scenario: User designs a job
    Given I go to "/"
    When I log in as "demo" with "demo" password
    When I click "design"
    Then I should see "drag tools here to begin"