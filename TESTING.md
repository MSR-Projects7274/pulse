# Pulse Testing

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
