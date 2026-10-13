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
