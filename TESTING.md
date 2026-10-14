# Pulse Testing

This document contains the detailed testing evidence for Pulse.

Testing is recorded separately from the main README so that individual test cases, validation evidence and production checks can be documented in enough detail without obscuring the project's general documentation.

User-story validation screenshots remain in `README.md`. They demonstrate implementation of the planned user experience but are kept separate from functional testing evidence.

## Testing Contents

- [Testing Strategy](#testing-strategy)
- [Production Smoke Test Checklist](#production-smoke-test-checklist)
- [Manual Testing Log](#manual-testing-log)
- [Automated Testing](#automated-testing)
- [Validation](#validation)
- [Responsive and Browser Testing](#responsive-and-browser-testing)
- [Production CRUD Testing](#production-crud-testing)
- [Authentication and Permissions Testing](#authentication-and-permissions-testing)
- [Error Page Testing](#error-page-testing)
- [Bugs Found and Fixed](#bugs-found-and-fixed)
- [Known Bugs](#known-bugs)

---

## Testing Strategy

Pulse is tested at several levels so that both individual application behaviour and the deployed production system can be verified.

| Testing Area | Purpose | Evidence Status |
| --- | --- | --- |
| Production smoke testing | Confirms that the deployed application and its critical user flows work after deployment. | Checklist already established; final execution evidence will be recorded during the final audit. |
| Manual functional testing | Verifies real user actions and their resulting application/database behaviour. | Production testing log already contains completed tests. |
| Automated testing | Verifies application logic and regression-sensitive behaviour through Django's test framework. | 32 automated tests passed successfully with no failures or Django system-check issues. |
| Validation | Checks HTML, CSS and Python quality using appropriate validation and linting tools. | W3C HTML and CSS validation and Flake8 Python validation completed successfully. |
| Responsive and browser testing | Verifies layout and interaction behaviour across representative viewport sizes and browsers. | Responsive testing passed across six representative viewport sizes and Firefox, Chrome and Edge. |
| Production CRUD testing | Confirms that create, read, update and delete operations behave correctly against the deployed application. | Existing production evidence will be consolidated into a dedicated section. |
| Authentication and permissions | Verifies account flows, protected actions and ownership restrictions. | Existing production evidence will be consolidated into a dedicated section. |
| Error handling | Verifies custom error pages and graceful handling of invalid or forbidden requests. | Existing evidence will be consolidated into a dedicated section. |
| Bug tracking | Records significant bugs found, their fixes and any known remaining issues. | Final evidence will be added after the testing audit is complete. |

---

## Production Smoke Test Checklist

This checklist is used to verify the deployed Pulse application on Heroku after deployment.

The production smoke test must be performed against the live Heroku application rather than localhost.

| ID | Test | Expected Result | Result |
| --- | --- | --- | --- |
| PS-01 | Open the deployed homepage. | Homepage loads successfully without a 500 error. | Pending |
| PS-02 | Register a new account. | Account is created and the user can access Pulse. | Pending |
| PS-03 | Log out and log back in. | Authentication succeeds and the user is returned to the expected page. | Pending |
| PS-04 | Open an existing post. | Post detail page loads successfully. | Pending |
| PS-05 | Create a text-only post. | Post is created and appears in the feed. | Pending |
| PS-06 | Create a post with an image. | Post and uploaded image appear correctly. | Pending |
| PS-07 | Edit an owned post. | Updated post content is displayed correctly. | Pending |
| PS-08 | Add a comment. | Comment appears on the post. | Pending |
| PS-09 | Edit an owned comment. | Updated comment appears correctly. | Pending |
| PS-10 | Delete an owned comment. | Comment is removed. | Pending |
| PS-11 | Upvote, downvote, switch and remove a vote. | Vote state and score update correctly. | Pending |
| PS-12 | Open the user's profile. | Profile loads with the correct posts and comments. | Pending |
| PS-13 | Attempt to edit another user's post. | Request is denied with the branded 403 page. | Pending |
| PS-14 | Attempt to edit another user's comment. | Request is denied with the branded 403 page. | Pending |
| PS-15 | Visit a nonexistent URL. | Branded 404 page is displayed. | Pending |
| PS-16 | Delete an owned post. | Post is removed successfully. | Pending |
| PS-17 | Check browser DevTools during the smoke test. | No unexpected console errors or 500 network responses occur. | Pending |

## Manual Testing Log

The following manual tests record production verification completed against the live Heroku deployment during the remediation process.

| Test ID | User Story | Preconditions | Action | Expected Result | Actual Result | Pass / Fail | Environment |
| --- | --- | --- | --- | --- | --- | --- | --- |
| MT-01 | As a new user, I can register and access Pulse. | No existing account with the test username. | Register a completely new account. | Account is created and Pulse loads normally. | New production account created successfully and application loaded normally. | Pass | Heroku Production |
| MT-02 | As a user, I can log out and log back in. | Registered production test account. | Log out, then log back in with the same credentials. | Authentication succeeds without errors. | Logout and subsequent login both succeeded. | Pass | Heroku Production |
| MT-03 | As a user, I can create, edit and delete my posts. | Logged-in production test account. | Create a post, edit it, then delete it through the UI while checking Django Admin after each action. | Backend row is created, updated and removed correctly. | Post appeared in Admin, reflected edits, and disappeared after deletion. | Pass | Heroku Production |
| MT-04 | As a user, I can create a post containing an image. | Logged-in production test account. | Create an image post and view it before and after a dyno restart. | Post and image remain available after restart. | Post and image persisted successfully after restart. Image display sizing requires later UI polish. | Pass | Heroku Production |
| MT-05 | As a user, I can create, edit and delete my comments. | Logged-in production test account and existing post. | Create a comment, edit it, then delete it while checking Django Admin after each action. | Backend row is created, updated and removed correctly. | Comment appeared in Admin, reflected edits, and disappeared after deletion. | Pass | Heroku Production |
| MT-06 | As a user, I can change and remove my post vote. | Logged-in production test account and existing post. | Upvote, switch to downvote, then remove the vote while inspecting PostVote through the production Django shell. | One vote row changes from 1 to -1 and is removed when toggled off. | Existing vote row changed correctly and was removed completely. | Pass | Heroku Production |
| MT-07 | As a user, I can change and remove my comment vote. | Logged-in production test account and existing comment. | Upvote, switch to downvote, then remove the vote while inspecting CommentVote through the production Django shell. | One vote row changes state and is removed when toggled off. | Comment vote changed and was removed correctly. | Pass | Heroku Production |
| MT-08 | As a user, I can view my profile. | Logged-in production test account. | Open the user's profile from the homepage. | Profile displays correctly with the user's activity. | Profile loaded correctly. Navigation currently requires returning to the homepage because post-detail pages do not provide a profile link. | Pass | Heroku Production |
| MT-09 | As a user, I cannot edit another user's content. | Logged in as a user who does not own the target content. | Attempt to edit another user's post and comment. | Access is denied using the branded 403 page. | Both permission checks returned the branded 403 page. | Pass | Heroku Production |
| MT-10 | As a user, invalid URLs fail gracefully. | Live application available. | Visit a deliberately nonexistent URL. | Branded 404 page is displayed instead of a server error. | Custom Pulse 404 page displayed correctly. | Pass | Heroku Production |
| MT-11 | As a user, I receive current production assets rather than stale cached files. | Private browser window with DevTools open and cache disabled. | Navigate through homepage, post detail, create post, profile, community, 403 and 404 pages. | Pages and static assets load correctly with no unexpected errors. | All checked pages loaded normally with no unexpected console or network errors. | Pass | Heroku Production, Private Window, Cache Disabled |
| MT-12 | As a user, my data survives a Heroku dyno restart. | Production account and persistence-test post already exist. | Restart all Heroku dynos, then reload and inspect existing data and image media. | User data, posts and uploaded media remain available. | Account, existing content and uploaded image all survived the restart. | Pass | Heroku Production |

## Automated Testing

Pulse includes automated tests built using Django's `TestCase` framework. The test suite covers core authentication, content, permissions, voting, validation and error-handling behaviour so that changes to the application can be checked for regressions.

The automated tests are located in:

- `pulse/accounts/tests.py`
- `pulse/departments/tests.py`
- `pulse/posts/tests.py`

The complete automated test suite is run from the project root with:

```bash
python manage.py test
```

### Test Result

The final automated test run completed successfully:

```text
Found 32 test(s).
System check identified no issues (0 silenced).
................................
----------------------------------------------------------------------
Ran 32 tests in 28.472s

OK
```

**Result: 32 tests passed, with no test failures or Django system-check issues.**

The automated suite includes coverage for:

- successful and unsuccessful user registration;
- successful and failed login;
- login redirect behaviour;
- POST-based logout and rejection of GET logout requests;
- homepage and post-detail access for new users;
- post creation, including image uploads;
- post editing, image preservation and replacement;
- post deletion and ownership permissions;
- comment creation, editing, deletion and validation;
- post and comment voting, including switching and removing votes;
- rejection of invalid vote values;
- community pages and invalid community handling;
- user profiles with no existing activity;
- custom 403 and 404 responses;
- search across posts and communities.

Automated testing complements the manual production checks documented elsewhere in this file. The automated suite verifies repeatable application behaviour in Django's isolated test environment, while production testing confirms the same broader application behaves correctly after deployment.

## Validation

### HTML - W3C Nu HTML Checker

Rendered HTML was checked using the **W3C Nu HTML Checker**.

Public pages were validated using the deployed Heroku application. Pages requiring authentication were checked using their rendered page source so that the validator received the final HTML generated by Django rather than Django template syntax.

Representative pages validated included:

- homepage / post feed;
- login;
- registration;
- community search;
- post detail;
- user profile;
- department / community pages;
- create post;
- edit post;
- delete post;
- delete comment;
- custom 404 page.

The validation pass identified one heading-level warning on the Create Post page. The page used an `<h2>` as its primary heading, which was corrected to `<h1>`. The rendered page was then validated again successfully.

The custom 404 page was validated using its rendered source because validating the deployed URL directly correctly returns an HTTP 404 status before the validator can treat it as a normal successful page response.

Following the correction and revalidation, the representative rendered HTML pages completed validation with **no remaining HTML errors or warnings**.

### CSS - W3C CSS Validation Service

Both custom Pulse stylesheets were checked using the **W3C CSS Validation Service**:

- `static/css/style.css`
- `static/css/auth.css`

Both stylesheets completed validation successfully with **no CSS errors**.

**Result:**

```text
static/css/style.css: No errors
static/css/auth.css: No errors
```

### Python - Flake8

The Pulse Python source was checked using **Flake8 7.4.1**.

The project-wide validation command was:

```bash
python -m flake8 manage.py pulse --exclude=.venv,*/migrations/*,staticfiles
```

The initial validation run identified **42 findings**. These were code-quality and formatting issues rather than application-logic failures, including unused imports, missing end-of-file newlines, blank-line spacing and lines exceeding the configured 79-character limit.

The cleanup included:

- removing unused imports;
- removing unused Django scaffold files that contained no application code;
- correcting blank-line spacing between classes, methods and top-level view sections;
- adding missing end-of-file newlines;
- wrapping long URL declarations and strings without changing their values or behaviour;
- removing an unused `Sum` import from the post views.

After the cleanup, the same Flake8 command completed with **no output**, confirming that no Flake8 findings remained in the checked Python source.

The complete Django automated test suite was then run again to ensure that the formatting and cleanup changes had not altered application behaviour:

```bash
python manage.py test
```

The regression run completed successfully:

```text
Ran 32 tests in 29.735s

OK
```

**Result: Flake8 passed with no remaining findings and all 32 automated tests continued to pass.**

## Responsive and Browser Testing

Manual responsive and cross-browser testing was completed against the **live Heroku deployment**.

Responsive behaviour was checked using representative desktop, tablet and mobile viewport sizes. The testing focused on ensuring that navigation, content, forms and interactive controls remained usable without clipping, overlapping or unintended horizontal scrolling.

### Responsive Viewport Testing

| Viewport | Representative Device Type | Result |
| --- | --- | --- |
| 1440 × 900 | Desktop | Pass |
| 1024 × 768 | Laptop / small desktop | Pass |
| 768 × 1024 | Tablet | Pass |
| 425 × 915 | Large mobile | Pass |
| 375 × 667 | Mobile | Pass |
| 320 × 568 | Small mobile | Pass |

The responsive checks covered representative pages and user flows including:

- homepage / post feed;
- post detail;
- create post;
- community search;
- user profile;
- login;
- registration;
- custom 404 page.

Across the tested viewport sizes:

- navigation remained accessible and usable;
- page content remained readable without unintended horizontal scrolling;
- post and profile content remained within their containers;
- forms and form controls fitted within the available viewport;
- buttons and voting controls remained accessible;
- images scaled within their containers;
- content did not overlap or become clipped;
- authentication and search pages remained usable;
- the custom error page continued to display correctly.

### Browser Testing

The deployed application was also manually checked using the current desktop versions of:

| Browser | Result |
| --- | --- |
| Mozilla Firefox | Pass |
| Google Chrome | Pass |
| Microsoft Edge | Pass |

The main navigation, post feed, post detail, forms, profile pages and interactive controls behaved consistently across the tested browsers.

**Result: Responsive and cross-browser testing completed successfully with no layout-breaking or browser-specific issues identified during the test pass.**

## Production CRUD Testing

Dedicated production CRUD evidence is documented during the final testing audit.

## Authentication and Permissions Testing

Dedicated authentication, ownership and permission evidence is documented during the final testing audit.

## Error Page Testing

Custom 403, 404 and 500 error-page evidence is documented during the final testing audit.

## Bugs Found and Fixed

Significant bugs identified and resolved during development and remediation are documented during the final testing audit.

## Known Bugs

Any issues remaining after final testing are documented here.
