Feature: User can see login to site
Scenario: Successful Login
    Given I go to "/"
    When I log in as "demo" with "demo" password
    Then I should see "Use selection to auto-filter?"

Scenario: UnSuccessful Login
    Given I go to "/"
    When I log in as "demo" with "iamwrong" password
    Then I should see "Invalid login credentials"
