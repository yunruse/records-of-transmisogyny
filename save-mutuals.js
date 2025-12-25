// This script will print to the console your Tumblr mutuals ready for saving
// with thanks to https://www.tumblr.com/dragongirlsnout/801521136958636032

(async () => {
    const mutuals = [];
    let nextUrl = '/v2/user/following?fields[blogs]=name,?is_following_you,?duration_blog_following_you,?duration_following_blog';
    while (nextUrl) {
        await window.tumblr.apiFetch(nextUrl).then(({ response: { blogs, links } }) => {
            mutuals.push(...blogs.filter(({ isFollowingYou }) => !!isFollowingYou));
            nextUrl = links?.next?.href;
        });
    }
    console.log(mutuals);
})();