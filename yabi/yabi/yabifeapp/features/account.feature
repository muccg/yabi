Feature: User can see account information
Scenario: User views account info
    Given I go to "/"
    When I log in as "demo" with "demo" password
    When I click "account"
    Then I should see "Change Password"