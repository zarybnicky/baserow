# Changelog

## Released (2021-03-01)

* Redesigned the left sidebar.
* Fixed error when a very long user file name is provided when uploading.
* Upgraded DRF Spectacular dependency to the latest version.
* Added single select field form option validation.
* Changed all cookies to SameSite=lax.
* Fixed the "Ignored attempt to cancel a touchmove" error.
* Refactored the has_user everywhere such that the raise_error argument is used when
  possible.
* Added Baserow Cloudron app.
* Fixed bug where a single select field without options could not be converted to a
  another field.
* Fixed bug where the Editable component was not working if a prent a user-select:
  none; property.
* Fail hard when the web-frontend can't reach the backend because of a network error.
* Use UTC time in the date picker.
* Refactored handler get_* methods so that they never check for permissions.
* Made it possible to configure SMTP settings via environment variables.
* Added field name to the public REST API docs.
* Made the public REST API docs compatible with smaller screens.
* Made it possible for the admin to disable new signups.
* Reduced the amount of queries when using the link row field.
* Respect the date format when converting to a date field.
* Added a field type filename contains filter.

## Released (2021-02-04)

* Upgraded web-frontend dependencies.
* Fixed bug where you could not convert an existing field to a single select field
  without select options.
* Fixed bug where is was not possible to create a relation to a table that has a single
  select as primary field.
* Implemented real time collaboration.
* Added option to hide fields in a grid view.
* Keep token usage details.
* Fixed bug where an incompatible row value was visible and used while changing the
  field type.
* Fixed bug where the row in the RowEditModel was not entirely reactive and wouldn't be
  updated when the grid view was refreshed.
* Made it possible to invite other users to a group.

## Released (2021-01-06)

* Allow larger values for the number field and improved the validation.
* Fixed bug where if you have no filters, but the filter type is set to `OR` it always
  results in a not matching row state in the web-frontend.
* Fixed bug where the arrow navigation didn't work for the dropdown component in
  combination with a search query.
* Fixed bug where the page refreshes if you press enter in an input in the row modal.
* Added filtering by GET parameter to the rows listing endpoint.
* Fixed drifting context menu.
* Store updated and created timestamp for the groups, applications, tables, views,
  fields and rows.
* Made the file name editable.
* Made the rows orderable and added the ability to insert a row at a given position.
* Made it possible to include or exclude specific fields when listing rows via the API.
* Implemented a single select field.
* Fixed bug where inserting above or below a row created upon signup doesn't work
  correctly.

## Released (2020-12-01)

* Added select_for_update where it was still missing.
* Fixed API docs scrollbar size issue.
* Also lint the backend tests.
* Implemented a switch to disable all filters without deleting them.
* Made it possible to order by fields via the rows listing endpoint.
* Added community chat to the readme.
* Made the cookies strict and secure.
* Removed the redundant _DOMAIN variables.
* Set un-secure lax cookie when public web frontend url isn't over a secure connection.
* Fixed bug where the sort choose field item didn't have a hover effect.
* Implemented a file field and user files upload.
* Made it impossible for the `link_row` field to be a primary field because that can
  cause the primary field to be deleted.

## Released (2020-11-02)

* Highlight the row of a selected cell.
* Fixed error when there is no view.
* Added Ubuntu installation guide documentation.
* Added Email field.
* Added importer abstraction including a CSV and tabular paste importer.
* Added ability to navigate dropdown menus with arrow keys.
* Added confirmation modals when the user wants to delete a group, application, table,
  view or field.
* Fixed bug in the web-frontend URL validation where a '*' was invalidates.
* Made it possible to publicly expose the table data via a REST API.

## Released (2020-10-06)

* Prevent adding a new line to the long text field in the grid view when selecting the
  cell by pressing the enter key.
* Fixed The table X is not found in the store error.
* Fixed bug where the selected name of the dropdown was not updated when that name was
  changed.
* Fixed bug where the link row field is not removed from the store when the related
  table is deleted.
* Added filtering of rows per view.
* Fixed bug where the error message of the 'Select a table to link to' was not always
  displayed.
* Added URL field.
* Added sorting of rows per view.

## Released (2020-09-02)

* Added contribution guidelines.
* Fixed bug where it was not possible to change the table name when it contained a link
  row field.

## Released (2020-08-31)

* Added field that can link to the row of another table.
* Fixed bug where the text_default value changed to None if not provided in a patch
  request.
* Block non web frontend domains in the base url when requesting a password reset
  email.
* Increased the amount of password characters to 256 when signing up.
* Show machine readable error message when the signature has expired.

## Released (2020-07-20)

* Added raises attribute to the docstrings.
* Added OpenAPI docs.
* Refactored all SCSS classes to BEM naming.
* Use the new long text field, date field and view's field options for the example 
  tables when creating a new account. Also use the long text field when creating a new 
  table.
* Removed not needed api v0 namespace in url and python module.
* Fixed keeping the datepicker visible in the grid view when selecting a date for the 
  first time.
* Improved API 404 errors by providing a machine readable error.
* Added documentation markdown files.
* Added cookiecutter plugin boilerplate.

## Released (2020-06-08)

* Fixed not handling 500 errors.
* Prevent row context menu when right clicking on a field that's being edited.
* Added row modal editing feature to the grid view.
* Made it possible to resize the field width per view.
* Added validation and formatting for the number field.
* Cancel the editing state of a fields when the escape key is pressed.
* The next field is now selected when the tab character is pressed when a field is
  selected.
* Changed the styling of the notification alerts.
* Fixed error when changing field type and the data value wasn't in the correct
  format.
* Update the field's data values when the type changes.
* Implemented reset forgotten password functionality.
* Fill a newly created table with some initial data.
* Enabled the arrow keys to navigate through the fields in the grid view.
* Fixed memory leak bug.
* Use environment variables for all settings.
* Normalize the users email address when signing up and signing in.
* Use Django REST framework status code constants instead of integers.
* Added long text field.
* Fixed not refreshing token bug and improved authentication a little bit.
* Introduced copy, paste and delete functionality of selected fields.
* Added date/datetime field.
* Improved grid view scrolling for touch devices.
* Implemented password change function and settings popup.
