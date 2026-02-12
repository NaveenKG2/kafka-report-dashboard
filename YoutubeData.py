from googleapiclient.discovery import build

# Replace with your API key
api_key = 'AIzaSyDFQA2ENuHaQl4DMEXgLVzNK0vMPnCewRk'
video_id = 'KP_LTFjTq4M'

search_text1 = 'Jithanka'
search_text2 = 'C-04'
search_text3 = 'Bhoomi'
search_text4 = 'C-02'
search_text5 = 'Ruthvik'
search_text6 = 'C-08'
search_text7 = 'Anagha'
search_text8 = 'C-10'
search_text9 = 'Eshan'
search_text10 = 'C-06'

youtube = build('youtube', 'v3', developerKey=api_key)

def get_comments(video_id, search_text1,search_text2):
    comments = []
    next_page_token = None

    while True:
        request = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            pageToken=next_page_token,
            maxResults=100
        )
        response = request.execute()

        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            if search_text1.lower() in comment.lower():
                comments.append(comment)
            if search_text2.lower() == comment.lower():
                comments.append(comment)

                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break
    return comments

def get_unique_commenters(video_id, search_text1,search_text2):
    unique_users = set()
    next_page_token = None

    while True:
        request = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            pageToken=next_page_token,
            maxResults=100
        )
        response = request.execute()

        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            author = item['snippet']['topLevelComment']['snippet']['authorChannelId']['value']
            if search_text1.lower() in comment.lower():
                unique_users.add(author)
                if search_text2.lower() == comment.lower():
                    unique_users.add(author)

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    return unique_users

Jithankacomments = get_comments(video_id, search_text1,search_text2)
Junique_users = get_unique_commenters(video_id, search_text1,search_text2)
Bhoomicomments = get_comments(video_id, search_text3,search_text4)
Bunique_users = get_unique_commenters(video_id, search_text3,search_text4)
Ruthvikcomments = get_comments(video_id, search_text5,search_text6)
Runique_users = get_unique_commenters(video_id,search_text5,search_text6)
Anaghacomments = get_comments(video_id, search_text7,search_text8)
Aunique_users = get_unique_commenters(video_id,search_text7,search_text8)
Eshancomments = get_comments(video_id, search_text9,search_text10)
Eunique_users = get_unique_commenters(video_id,search_text9,search_text10)

print(f"Number of comments containing '{search_text1}' and exact match {search_text2}: {len(Jithankacomments)}")
print(f"Number of unique users who voted for '{search_text1}': {len(Junique_users)}")
print(f"Number of comments containing '{search_text3}' and exact match {search_text4}: {len(Bhoomicomments)}")
print(f"Number of unique users who voted for '{search_text3}': {len(Bunique_users)}")
print(f"Number of comments containing '{search_text5}' and exact match {search_text6}: {len(Ruthvikcomments)}")
print(f"Number of unique users who voted for '{search_text5}': {len(Runique_users)}")
print(f"Number of comments containing '{search_text7}' and exact match {search_text8}: {len(Anaghacomments)}")
print(f"Number of unique users who voted for '{search_text7}': {len(Aunique_users)}")
print(f"Number of comments containing '{search_text9}' and exact match {search_text10}: {len(Eshancomments)}")
print(f"Number of unique users who voted for '{search_text9}': {len(Eunique_users)}")