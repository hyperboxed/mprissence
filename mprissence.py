import time
import dbus
from pypresence import Presence
from pypresence.types import ActivityType, StatusDisplayType
import requests
import urllib.parse
import base64

CLIENT_ID = '1441078347429052530'
IMGUR_CLIENT_ID = 'd70305e7c3ac5c6' 

def get_elisa_metadata():
    try:
        session_bus = dbus.SessionBus()
        player = session_bus.get_object('org.mpris.MediaPlayer2.elisa', '/org/mpris/MediaPlayer2')
        interface = dbus.Interface(player, 'org.freedesktop.DBus.Properties')
        
        metadata = interface.Get('org.mpris.MediaPlayer2.Player', 'Metadata')
        status = interface.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus')
        
        return interface, status, metadata
    except dbus.exceptions.DBusException:
        return None, None, None

def search_itunes(query):
    try:
        url = f"https://itunes.apple.com/search?term={urllib.parse.quote(query)}&media=music&limit=1"
        response = requests.get(url, timeout=3)
        data = response.json()
        if data['resultCount'] > 0:
            return data['results'][0]['artworkUrl100'].replace('100x100', '512x512')
    except Exception as e:
        print(f"Error fetching from iTunes for query '{query}': {e}")

    return None

def upload_to_imgur(image_path):
    try:
        b64_image = None
        source_desc = "unknown"

        # local file (file://)
        if image_path and image_path.startswith('file://'):
            local_path = image_path.replace('file://', '')
            local_path = urllib.parse.unquote(local_path)
            source_desc = local_path
            with open(local_path, 'rb') as image_file:
                b64_image = base64.b64encode(image_file.read())
        
        # embedded base64 data (data:image...)
        elif image_path and image_path.startswith('data:image'):
            source_desc = "embedded base64 data"
            # we need everything after the comma
            try:
                b64_image = image_path.split(',', 1)[1]
            except IndexError:
                print("Error parsing data URI")
                return None, None
        
        else:
            return None, None

        # upload to imgur
        if b64_image:
            headers = {'Authorization': f'Client-ID {IMGUR_CLIENT_ID}'}
            # Imgur accepts base64 string without headers
            data = {'image': b64_image, 'type': 'base64'}
            
            print(f"Uploading cover to Imgur ({source_desc})...")
            response = requests.post('https://api.imgur.com/3/image', headers=headers, data=data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()['data']
                return data['link'], data['deletehash']
            else:
                print(f"Imgur upload failed: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Error uploading to Imgur: {e}")
    
    return None, None

def delete_from_imgur(deletehash):
    if not deletehash:
        return
    try:
        headers = {'Authorization': f'Client-ID {IMGUR_CLIENT_ID}'}
        requests.delete(f'https://api.imgur.com/3/image/{deletehash}', headers=headers, timeout=10)
        print(f"Deleted old cover from Imgur")
    except Exception as e:
        print(f"Error deleting from Imgur: {e}")

def main():
    rpc = Presence(CLIENT_ID)

    connected = False
    while not connected:
        try:
            rpc.connect()
            connected = True
            print("Discord RPC connected!")
        except Exception as e:
            # waiting 5 seconds before retrying again
            time.sleep(5)

    last_track = ""
    last_deletehash = None
    last_status = "" 
    last_sent_start_time = 0
    
    current_large_image = "elisa_logo"
    current_large_text = "Elisa Music Player"
    current_small_image = "play_icon"
    current_small_text = "Playing"
    current_details = ""
    current_state = ""

    while True:
        interface, status, metadata = get_elisa_metadata()
        
        if status == 'Playing':
            # obtain data
            title = str(metadata.get('xesam:title', 'Unknown Title'))
            artist = str(metadata.get('xesam:artist', ['Unknown Artist'])[0]) 
            album = str(metadata.get('xesam:album', ''))
            mpris_art_url = str(metadata.get('mpris:artUrl', ''))
            length = int(metadata.get('mpris:length', 0))
            
            # get position for timeline
            current_position = interface.Get('org.mpris.MediaPlayer2.Player', 'Position')
            
            start_time = None
            end_time = None
            if current_position is not None:
                # calculate the "start" timestamp relative to now
                start_time = time.time() - (current_position / 1000000)
                if length:
                    end_time = start_time + (length / 1000000)
            
            details_str = f"{title}"
            state_str = f"{artist}"
            large_text_display = f"{album}" if album else "Elisa Music Player"
            
            # ---> NEW TRACK DETECTED
            if title != last_track:
                # print(f"Now playing: {title} - {artist}")
                
                cover_url = None

                # 1. check for remote url (http)
                if mpris_art_url.startswith('http'):
                    cover_url = mpris_art_url
                
                # 2. try iTunes search
                if not cover_url:
                    # We are about to search/change covers, so clean up old Imgur upload
                    if last_deletehash:
                        delete_from_imgur(last_deletehash)
                        last_deletehash = None
                    
                    # Artist + Album
                    if album:
                        cover_url = search_itunes(f"{artist} {album}")
                    
                    # Artist + Title (fallback)
                    if not cover_url:
                        print(f"Album art not found. Fallback search: {artist} {title}")
                        cover_url = search_itunes(f"{artist} {title}")

                # 3. upload local file or embedded data to Imgur
                # only runs if both HTTP check and iTunes search failed
                if not cover_url and mpris_art_url.startswith(('file://', 'data:image')):
                    print("iTunes search failed. Uploading local/embedded art to Imgur.")
                    
                    # ensure cleanup (just in case)
                    if last_deletehash:
                        delete_from_imgur(last_deletehash)
                        last_deletehash = None
                        
                    cover_url, new_deletehash = upload_to_imgur(mpris_art_url)
                    if new_deletehash:
                        last_deletehash = new_deletehash
                
                # set current state vars
                if cover_url:
                    current_large_image = cover_url
                    current_small_image = "elisa_logo"
                    current_small_text = "Elisa Music Player"
                else:
                    current_large_image = "elisa_logo"
                    current_small_image = "play_icon"
                    current_small_text = "Playing"
                
                current_large_text = large_text_display
                current_details = details_str
                current_state = state_str

                # update RPC
                rpc.update(
                    state=current_state,
                    details=current_details,
                    large_image=current_large_image,
                    large_text=current_large_text,
                    small_image=current_small_image,
                    small_text=current_small_text,
                    activity_type=ActivityType.LISTENING,
                    start=start_time,
                    end=end_time,
                    status_display_type=StatusDisplayType.STATE
                )
                
                last_track = title
                last_status = "Playing"
                last_sent_start_time = start_time

            # ---> SAME TRACK (check for seek or resume)
            else:
                # calculate drift: difference between the "start time" sent to Discord and current calculation
                # if user seeks forward, "start_time" moves forward
                time_drift = abs(start_time - last_sent_start_time) if last_sent_start_time else 0
                
                should_update = False
                
                # case a: resumed from pause
                if last_status != "Playing":
                    # print("Resumed from pause - updating RPC")
                    should_update = True
                
                # case b: seek detected (e.g. slider moved > 2 seconds)
                elif time_drift > 2:
                    # print(f"Seek detected (drift: {time_drift:.2f}s) - updating timestamp")
                    should_update = True

                if should_update:
                    rpc.update(
                        state=current_state,
                        details=current_details,
                        large_image=current_large_image,
                        large_text=current_large_text,
                        small_image=current_small_image,
                        small_text=current_small_text,
                        activity_type=ActivityType.LISTENING,
                        start=start_time,
                        end=end_time,
                        status_display_type=StatusDisplayType.STATE
                    )
                    last_sent_start_time = start_time
                    last_status = "Playing"

        elif status == 'Paused':
            if last_status != "Paused":
                rpc.clear()
                last_status = "Paused"
            # do not clear last_track so we don't re-fetch cover art on resume
        
        else:
            # elisa is closed or stopped
            if last_status != "Stopped":
                rpc.clear()
                last_status = "Stopped"
                last_track = ""
                # clean up Imgur if player stops
                if last_deletehash:
                    delete_from_imgur(last_deletehash)
                    last_deletehash = None

        time.sleep(1)

if __name__ == '__main__':
    main()