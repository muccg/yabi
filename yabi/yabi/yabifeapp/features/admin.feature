Feature: Admin can log into Admin Site
Scenario: Admin views admin page
    Given I go to "/"
    When I log in as "admin" with "admin" password
    Given I go to "/admin-pane"
    Then I should see "Site administration"