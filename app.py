import praw
import streamlit as st
import random
import time

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
st.title("Reddit Image Slideshow with Enhancements")

# Input subreddit name
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

            # Initialize session state variables
            if "current_index" not in st.session_state:
                st.session_state.current_index = 0
            if "play_slideshow" not in st.session_state:
                st.session_state.play_slideshow = False

            # Slideshow controls
            st.sidebar.header("Slideshow Controls")
            play_pause = st.sidebar.button(
                "Play" if not st.session_state.play_slideshow else "Pause"
            )
            if play_pause:
                st.session_state.play_slideshow = not st.session_state.play_slideshow

            next_button = st.sidebar.button("Next")
            prev_button = st.sidebar.button("Previous")
            delay = st.sidebar.slider("Set delay (seconds):", 1, 10, 3)

            # Handle next and previous button clicks
            if next_button:
                st.session_state.current_index = (
                    st.session_state.current_index + 1
                ) % len(all_images)
                st.session_state.play_slideshow = False  # Pause slideshow on manual navigation

            if prev_button:
                st.session_state.current_index = (
                    st.session_state.current_index - 1
                ) % len(all_images)
                st.session_state.play_slideshow = False  # Pause slideshow on manual navigation

            # Display current image
            placeholder = st.empty()
            while True:
                with placeholder:
                    current_image = all_images[st.session_state.current_index]
                    st.image(current_image, caption=f"Image {st.session_state.current_index + 1}/{len(all_images)}", use_column_width=True)

                # Increment index if the slideshow is playing
                if st.session_state.play_slideshow:
                    st.session_state.current_index = (
                        st.session_state.current_index + 1
                    ) % len(all_images)
                else:
                    break  # Stop looping if slideshow is paused

                time.sleep(delay)  # Wait before displaying the next image
        else:
            st.write("No images found in this subreddit.")
    except Exception as e:
        st.error(f"Error fetching subreddit: {e}")
