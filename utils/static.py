class Static:
    QUERY_FIELDS = {'list_status', 'synopsis', 'my_list_status', 'id', 'title', 'alternative_titles', 'main_picture',
                    'start_date', 'end_date', 'mean', 'rank', 'popularity', 'num_list_users', 'num_scoring_users',
                    'nsfw', 'created_at', 'updated_at', 'status', 'genres', 'media_type', 'num_episodes',
                    'start_season', 'broadcast', 'source', 'average_episode_duration', 'rating', 'pictures',
                    'background', 'related_anime', 'related_manga', 'recommendations', 'studios', 'statistics'}
    QUERY_SORT_OPTIONS = {'list_score', 'list_updated_at', 'anime_title', 'anime_start_date'}
    QUERY_PARAMS = {'limit', 'offset', 'fields', 'status', 'sort', 'user_name', 'status'}
    ANIME_LIST_STATUSES = {'watching', 'completed', 'on_hold', 'dropped', 'plan_to_watch'}
