import praw
import streamlit as st
import time
import random

# Set up Reddit API
reddit = praw.Reddit(
    client_id="lCQo5bQ4ITrCIDFnwvApAA",
    client_secret="0tZuN3EdSsGfJmq58KI5BuL8qtFqTQ",
    user_agent="StreamlitRedditApp",
    check_for_async=False
)

# Function to check if a post has a gallery and extract image URLs
def get_gallery_images(post):
    image_urls = []
    if hasattr(post, "media_metadata"):  # Check if the post has media_metadata (gallery)
        for item in post.media_metadata.values():
            # Extract the "s" (source) URL, which is the highest quality
            image_url = item.get("s", {}).get("u")
            if image_url:
                image_urls.append(image_url.replace("&amp;", "&"))  # Fix URL encoding issues
    return image_urls

# Streamlit app
st.title("Reddit Image Slideshow")

subreddit_name = st.text_input("Enter subreddit name:", value="pics")  # Default to 'pics'
if subreddit_name:
    try:
        # Fetch the subreddit
        subreddit = reddit.subreddit(subreddit_name)
        st.write(f"Showing posts from: r/{subreddit_name}")

        # Collect all image URLs from the top 10 posts
        all_images = []
        for post in subreddit.hot(limit=10):  # Adjust limit as needed
            # Extract gallery images
            gallery_images = get_gallery_images(post)
            if gallery_images:
                all_images.extend(gallery_images)
            # Handle single image posts
            elif post.url.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                all_images.append(post.url)

        if all_images:
            # Randomize the image order
            random.shuffle(all_images)

            # Create a slideshow
            placeholder = st.empty()
            for image_url in all_images:
                with placeholder:
                    st.image(image_url, caption="Slideshow Image", use_column_width=True)
                time.sleep(3)  # Wait 3 seconds before showing the next image
        else:
            st.write("No images found in this subreddit.")
    except Exception as e:
        st.error(f"Error fetching subreddit: {e}")
