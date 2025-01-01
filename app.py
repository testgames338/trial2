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
st.title("Reddit Image Slideshow (Multiple Subreddits)")

# Input subreddit names
subreddit_names = st.text_input(
    "Enter subreddit names (separated by commas):", value="pics, wallpapers"
)

if subreddit_names:
    try:
        # Parse the subreddit names
        subreddit_list = [sub.strip() for sub in subreddit_names.split(",") if sub.strip()]

        # Collect images from all specified subreddits
        all_images = []
        for subreddit_name in subreddit_list:
            try:
                subreddit = reddit.subreddit(subreddit_name)
                for post in subreddit.hot(limit=20):  # Adjust limit as needed
                    # Extract gallery images
                    gallery_images = get_gallery_images(post)
                    if gallery_images:
                        all_images.extend(gallery_images)
                    # Handle single image posts
                    elif post.url.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        all_images.append(post.url)
            except Exception as e:
                st.error(f"Error fetching subreddit '{subreddit_name}': {e}")

        if all_images:
            # Randomize the image order
            random.shuffle(all_images)

            # Initialize session state variables
            if "current_index" not in st.session_state:
                st.session_state.current_index = 0
            if "play_slideshow" not in st.session_state:
                st.session_state.play_slideshow = False

            # Sidebar Controls
            st.sidebar.header("Slideshow Controls")
            play_pause = st.sidebar.button("Play/Pause")
            next_button = st.sidebar.button("Next")
            prev_button = st.sidebar.button("Previous")
            delay = st.sidebar.slider("Set delay (seconds):", 1, 10, 3)

            # Handle play/pause toggle
            if play_pause:
                st.session_state.play_slideshow = not st.session_state.play_slideshow

            # Handle navigation
            if next_button:
                st.session_state.current_index = (
                    st.session_state.current_index + 1
                ) % len(all_images)
                st.session_state.play_slideshow = False
            if prev_button:
                st.session_state.current_index = (
                    st.session_state.current_index - 1
                ) % len(all_images)
                st.session_state.play_slideshow = False

            # Placeholder for the slideshow
            placeholder = st.empty()

            # Slideshow logic
            if st.session_state.play_slideshow:
                for _ in range(len(all_images)):
                    with placeholder:
                        current_image = all_images[st.session_state.current_index]
                        st.image(
                            current_image,
                            caption=f"Image {st.session_state.current_index + 1}/{len(all_images)}",
                            use_column_width=True,
                        )
                    st.session_state.current_index = (
                        st.session_state.current_index + 1
                    ) % len(all_images)
                    time.sleep(delay)
            else:
                # Display the current image when paused
                current_image = all_images[st.session_state.current_index]
                with placeholder:
                    st.image(
                        current_image,
                        caption=f"Image {st.session_state.current_index + 1}/{len(all_images)}",
                        use_column_width=True,
                    )

        else:
            st.write("No images found in the specified subreddits.")
    except Exception as e:
        st.error(f"Error: {e}")
