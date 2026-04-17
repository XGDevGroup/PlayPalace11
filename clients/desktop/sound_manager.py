"""Sound and music manager for Play Palace v9 client."""

import logging
import os
import threading
import time
from sound_cacher import SoundCacher
from resource_paths import find_resource_path

LOG = logging.getLogger(__name__)


class AudioPlaylist:
    """Represents a playlist that can play either sounds or music tracks."""

    def __init__(
        self,
        tracks,
        audio_type,
        sound_manager,
        shuffle=False,
        repeats=1,
        auto_start=True,
        auto_remove=True,
    ):
        """
        Initialize an audio playlist.

        Args:
            tracks: List of audio file names to play
            audio_type: Either "sound" or "music" to determine playback method
            sound_manager: Reference to parent SoundManager
            shuffle: If True, shuffle the tracks randomly
            repeats: Number of times to repeat the playlist (0 for infinite, minimum 1 otherwise)
            auto_start: If True, automatically start playing the first track
            auto_remove: If True, automatically remove playlist when all repeats complete (ignored for infinite)
        """
        import random

        self.original_tracks = tracks.copy()
        self.tracks = tracks.copy()
        self.audio_type = audio_type  # "sound" or "music"
        self.sound_manager = sound_manager
        self.shuffle = shuffle
        self.repeats = (
            repeats if repeats == 0 else max(1, repeats)
        )  # 0 = infinite, minimum 1 otherwise
        self.current_repeat = 1  # Start at repeat 1
        self.track_index = 0
        self.is_active = False
        self.sync_handle = None
        self.callback = None
        self.current_stream = None
        self.auto_remove = auto_remove
        self.playlist_id = None  # Will be set by SoundManager when added

        # Shuffle if requested
        if shuffle:
            random.shuffle(self.tracks)

        # Auto-start if requested
        if auto_start and self.tracks:
            self.is_active = True
            self._play_next_track()

    def _play_next_track(self):
        """Play the next track in the playlist."""
        if not self.is_active or not self.tracks:
            return

        # Check if we've reached the end of the current iteration
        if self.track_index >= len(self.tracks):
            self.track_index = 0
            self.current_repeat += 1

            # Check if we've completed all repeats (only if not infinite)
            if self.repeats != 0 and self.current_repeat > self.repeats:
                self.stop()
                # Auto-remove if enabled
                if self.auto_remove and self.playlist_id:
                    self.sound_manager.remove_playlist(self.playlist_id)
                return

        # Remove any existing sync callback
        if self.sync_handle is not None and self.current_stream:
            try:
                from sound_lib.external.pybass import BASS_ChannelRemoveSync

                BASS_ChannelRemoveSync(self.current_stream.handle, self.sync_handle)
            except (AttributeError, OSError, RuntimeError) as exc:
                LOG.debug("Failed to remove audio sync: %s", exc)
            self.sync_handle = None

        # Get the next track
        track = self.tracks[self.track_index]

        # Create the stream based on audio type (but don't play yet)
        if self.audio_type == "music":
            self.sound_manager.music(track, looping=False, fade_out_old=False)
            self.current_stream = self.sound_manager.current_music
        else:  # sound
            # For sounds, we need to create the stream but not play it yet
            from sound_lib import stream

            track_path = os.path.join(self.sound_manager.sounds_folder, track)

            # Load from cache or create cache entry
            if track not in self.sound_manager.sound_cacher.cache:
                with open(track_path, "rb") as f:
                    import ctypes

                    self.sound_manager.sound_cacher.cache[track] = ctypes.create_string_buffer(
                        f.read()
                    )

            # Create stream without playing
            cache_buffer = self.sound_manager.sound_cacher.cache[track]
            self.current_stream = stream.FileStream(
                mem=True, file=cache_buffer, length=len(cache_buffer)
            )

        # Register BASS callback BEFORE playing (critical for very short sounds)
        if self.current_stream:
            try:
                from sound_lib.external.pybass import (
                    BASS_ChannelSetSync,
                    BASS_SYNC_END,
                    SYNCPROC,
                )

                # Create callback function
                self.callback = SYNCPROC(self._on_track_end_callback)

                # Register sync callback with BASS
                self.sync_handle = BASS_ChannelSetSync(
                    self.current_stream.handle, BASS_SYNC_END, 0, self.callback, None
                )
            except Exception:
                import traceback

                traceback.print_exc()
                self.sync_handle = None

        # Now play the stream (callback is already registered)
        if self.current_stream and self.audio_type == "sound":
            self.current_stream.play()
            self.sound_manager.sound_cacher.refs.append(self.current_stream)

        # Advance to next track index
        self.track_index += 1

    def _on_track_end_callback(self, handle, channel, data, user):
        """BASS callback function triggered when a track finishes playing."""
        if self.is_active and self.tracks:
            self._play_next_track()

    def stop(self):
        """Stop the playlist."""
        self.is_active = False

        # Remove BASS sync callback
        if self.sync_handle is not None and self.current_stream:
            try:
                from sound_lib.external.pybass import BASS_ChannelRemoveSync

                BASS_ChannelRemoveSync(self.current_stream.handle, self.sync_handle)
            except (AttributeError, OSError, RuntimeError) as exc:
                LOG.debug("Failed to remove audio sync: %s", exc)
            self.sync_handle = None
            self.callback = None

    def _get_track_duration(self, track):
        """
        Get the duration of a single track in seconds.

        Args:
            track: Track filename

        Returns:
            Duration in seconds, or 0 if unable to determine
        """
        try:
            track_path = os.path.join(self.sound_manager.sounds_folder, track)

            # Load the file to get its duration
            import ctypes
            from sound_lib import stream as sound_stream

            # Check cache first
            if track_path not in self.sound_manager.sound_cacher.cache:
                with open(track_path, "rb") as f:
                    self.sound_manager.sound_cacher.cache[track_path] = ctypes.create_string_buffer(
                        f.read()
                    )

            # Create temporary stream to get duration
            temp_stream = sound_stream.FileStream(
                mem=True,
                file=self.sound_manager.sound_cacher.cache[track_path],
                length=len(self.sound_manager.sound_cacher.cache[track_path]),
            )

            # Get length in seconds
            duration = temp_stream.length

            # Clean up temp stream
            temp_stream.free()

            return duration
        except Exception:
            import traceback

            traceback.print_exc()
            return 0

    def get_total_duration(self):
        """
        Get the total duration of all tracks in the playlist (in milliseconds).

        Returns:
            Total duration in milliseconds, or None if unable to calculate
        """
        try:
            total_duration_seconds = 0
            for track in self.tracks:
                total_duration_seconds += self._get_track_duration(track)

            return int(total_duration_seconds * 1000)
        except Exception:
            import traceback

            traceback.print_exc()
            return None

    def get_elapsed_duration(self):
        """
        Get the elapsed duration of the current iteration (in milliseconds).

        This includes:
        - The full duration of all completed tracks
        - The current position in the currently playing track (if any)

        Returns:
            Elapsed duration in milliseconds, or 0 if not playing
        """
        if not self.is_active:
            return 0

        try:
            elapsed_seconds = 0

            # Calculate current track index (account for the increment that happens after playing)
            current_playing_index = self.track_index - 1 if self.track_index > 0 else 0

            # Add duration of all completed tracks in this iteration
            for i in range(current_playing_index):
                elapsed_seconds += self._get_track_duration(self.tracks[i])

            # Add current position in currently playing track
            if self.current_stream and hasattr(self.current_stream, "position"):
                try:
                    elapsed_seconds += self.current_stream.position
                except (AttributeError, OSError, RuntimeError) as exc:
                    LOG.debug("Failed to read current stream position: %s", exc)

            return int(elapsed_seconds * 1000)
        except Exception:
            import traceback

            traceback.print_exc()
            return 0

    def get_remaining_duration(self):
        """
        Get the remaining duration of the current iteration (in milliseconds).

        This includes:
        - The remaining time in the currently playing track (if any)
        - The full duration of all remaining tracks

        Returns:
            Remaining duration in milliseconds, or 0 if not playing
        """
        if not self.is_active:
            return 0

        try:
            remaining_seconds = 0

            # Calculate current track index (account for the increment that happens after playing)
            current_playing_index = self.track_index - 1 if self.track_index > 0 else 0

            # Add remaining time in current track
            if self.current_stream:
                try:
                    current_track_duration = self._get_track_duration(
                        self.tracks[current_playing_index]
                    )
                    current_position = (
                        self.current_stream.position
                        if hasattr(self.current_stream, "position")
                        else 0
                    )
                    remaining_in_current = max(0, current_track_duration - current_position)
                    remaining_seconds += remaining_in_current
                except (AttributeError, OSError, RuntimeError) as exc:
                    LOG.debug("Failed to compute remaining duration: %s", exc)

            # Add duration of all remaining tracks
            for i in range(current_playing_index + 1, len(self.tracks)):
                remaining_seconds += self._get_track_duration(self.tracks[i])

            return int(remaining_seconds * 1000)
        except Exception:
            import traceback

            traceback.print_exc()
            return 0


class SoundManager:
    """Manages sound effects and background music playback."""

    def __init__(self):
        """Initialize the sound manager."""
        self.sound_cacher = SoundCacher()
        self.current_music = None
        self.current_music_name = None
        self.music_volume = 0.2
        self.sounds_folder = str(find_resource_path("sounds"))

        # Configurable menu sounds (can be changed by server)
        self.menuclick_sound = "menuclick.ogg"
        self.menuenter_sound = "menuenter.ogg"

        # Keep track of music fade thread (deprecated but kept for compatibility)
        self.fade_thread = None

        # Ambience system
        self.ambience_intro = None
        self.ambience_loop = None
        self.ambience_outro = None
        self.ambience_volume = 0.3
        self.ambience_thread = None
        self.ambience_stop_flag = False

        # Playlist system - now supports multiple playlists
        self.playlists = {}  # {playlist_id: AudioPlaylist}

    def play(self, sound_name, volume=1.0, pan=0.0, pitch=1.0):
        """
        Play a sound effect.

        Args:
            sound_name: Name of sound file (assumed to be in sounds/ folder)
            volume: Volume level 0.0-1.0
            pan: Pan -1.0 (left) to 1.0 (right)
            pitch: Pitch multiplier (1.0 = normal)

        Returns:
            The sound stream object
        """
        # Construct full path
        sound_path = os.path.join(self.sounds_folder, sound_name)

        try:
            return self.sound_cacher.play(sound_path, pan=pan, volume=volume, pitch=pitch)
        except Exception:
            return None

    def music(self, music_name: str, looping: bool = True, fade_out_old: bool = True):
        """
        Play background music with looping.

        Args:
            music_name: Name of music file (assumed to be in sounds/ folder)
            looping: whether to loop the music track or not.
            fade_out_old: Whether to fade out the current music before starting new (ignored, kept for compatibility)
        """
        # Don't restart if already playing this music
        if self.current_music_name == music_name and self.current_music:
            return

        # Stop old music immediately
        if self.current_music:
            try:
                self.current_music.stop()
            except (AttributeError, OSError, RuntimeError) as exc:
                LOG.debug("Failed to stop current music: %s", exc)

        # Start new music
        music_path = os.path.join(self.sounds_folder, music_name)
        try:
            self.current_music = self.sound_cacher.play(music_path, volume=self.music_volume)
            if self.current_music:
                self.current_music.looping = looping
            self.current_music_name = music_name
        except Exception:
            import traceback

            traceback.print_exc()
            self.current_music = None
            self.current_music_name = None

    def _fade_out_old_music_thread(self, old_music):
        """Fade out old music in a background thread."""

        def fade():
            try:
                start_volume = old_music.volume
                steps = 20
                for i in range(steps, -1, -1):
                    old_music.volume = start_volume * (i / steps)
                    time.sleep(0.05)
                old_music.stop()
            except (AttributeError, OSError, RuntimeError) as exc:
                LOG.debug("Failed to fade old music: %s", exc)

        # Start fade in background thread
        fade_thread = threading.Thread(target=fade, daemon=True)
        fade_thread.start()

    def _fade_out_music_blocking(self):
        """Fade out the current music and wait for it to complete."""
        if not self.current_music:
            return

        old_music = self.current_music

        try:
            start_volume = old_music.volume
            steps = 20
            for i in range(steps, -1, -1):
                old_music.volume = start_volume * (i / steps)
                time.sleep(0.05)
            old_music.stop()
        except (AttributeError, OSError, RuntimeError) as exc:
            LOG.debug("Failed to fade old music: %s", exc)

    def _fade_out_music(self):
        """Fade out the current music in a background thread."""
        if not self.current_music:
            return

        old_music = self.current_music

        def fade():
            try:
                start_volume = old_music.volume
                steps = 20
                for i in range(steps, -1, -1):
                    old_music.volume = start_volume * (i / steps)
                    time.sleep(0.05)
                old_music.stop()
            except (AttributeError, OSError, RuntimeError) as exc:
                LOG.debug("Failed to fade old music: %s", exc)

        # Start fade in background thread
        fade_thread = threading.Thread(target=fade, daemon=True)
        fade_thread.start()

    def stop_music(self, fade=True):
        """
        Stop the current music.

        Args:
            fade: Whether to fade out before stopping
        """
        if self.current_music:
            if fade:
                self._fade_out_music()
            else:
                try:
                    self.current_music.stop()
                except (AttributeError, OSError, RuntimeError) as exc:
                    LOG.debug("Failed to stop music: %s", exc)
            self.current_music = None
            self.current_music_name = None

    def set_music_volume(self, volume):
        """
        Set the music volume.

        Args:
            volume: Volume level 0.0-1.0
        """
        self.music_volume = max(0.0, min(1.0, volume))
        if self.current_music:
            try:
                self.current_music.volume = self.music_volume
            except (AttributeError, OSError, RuntimeError) as exc:
                LOG.debug("Failed to set music volume: %s", exc)

    def play_menuclick(self):
        """Play the menu click sound."""
        self.play(self.menuclick_sound, volume=0.5)

    def play_menuenter(self):
        """Play the menu enter/activate sound."""
        self.play(self.menuenter_sound, volume=0.5)

    def set_menuclick_sound(self, sound_name):
        """
        Set the menu click sound (called by server).

        Args:
            sound_name: Name of sound file in sounds/ folder
        """
        self.menuclick_sound = sound_name

    def set_menuenter_sound(self, sound_name):
        """
        Set the menu enter/activate sound (called by server).

        Args:
            sound_name: Name of sound file in sounds/ folder
        """
        self.menuenter_sound = sound_name

    def ambience(self, intro_name, loop_name, outro_name):
        """
        Play ambience with intro, loop, and outro.

        Args:
            intro_name: Name of intro sound file (or None to skip)
            loop_name: Name of loop sound file (required, will loop continuously)
            outro_name: Name of outro sound file (or None to skip)
        """
        # Stop any existing ambience (forcibly, without outro)
        self.stop_ambience(force=True)

        # Start ambience playback in background thread
        def play_ambience_sequence():
            try:
                # Check if audio is available (BASS initialized)
                from sound_cacher import o

                if o is None:
                    # Silent mode - skip ambience
                    return

                intro_path = os.path.join(self.sounds_folder, intro_name) if intro_name else None
                loop_path = os.path.join(self.sounds_folder, loop_name)
                outro_path = os.path.join(self.sounds_folder, outro_name) if outro_name else None

                # Play intro if provided
                if intro_path:
                    self.ambience_intro = self.sound_cacher.play(
                        intro_path, volume=self.ambience_volume
                    )
                    if self.ambience_intro:
                        # Wait for intro to finish
                        while self.ambience_intro.is_playing and not self.ambience_stop_flag:
                            time.sleep(0.1)
                        if self.ambience_stop_flag:
                            return

                # Play loop continuously
                # We need to create the stream, set looping, then play
                import ctypes
                from sound_lib import stream as sound_stream

                # Load loop sound
                if loop_path not in self.sound_cacher.cache:
                    with open(loop_path, "rb") as f:
                        self.sound_cacher.cache[loop_path] = ctypes.create_string_buffer(f.read())

                # Create stream and set looping before playing
                self.ambience_loop = sound_stream.FileStream(
                    mem=True,
                    file=self.sound_cacher.cache[loop_path],
                    length=len(self.sound_cacher.cache[loop_path]),
                )
                self.ambience_loop.volume = self.ambience_volume
                self.ambience_loop.looping = True
                self.ambience_loop.play()
                self.sound_cacher.refs.append(self.ambience_loop)

                if self.ambience_loop:
                    # Wait until stop is requested
                    while not self.ambience_stop_flag:
                        time.sleep(0.1)

                    # Stop loop
                    self.ambience_loop.looping = False
                    self.ambience_loop.stop()

                    # Play outro if provided
                    if outro_path:
                        self.ambience_outro = self.sound_cacher.play(
                            outro_path, volume=self.ambience_volume
                        )
                        if self.ambience_outro:
                            # Wait for outro to finish
                            while self.ambience_outro.is_playing:
                                time.sleep(0.1)

            except Exception:
                import traceback

                traceback.print_exc()
            finally:
                self.ambience_intro = None
                self.ambience_loop = None
                self.ambience_outro = None

        # Start in background thread
        self.ambience_stop_flag = False
        self.ambience_thread = threading.Thread(target=play_ambience_sequence, daemon=True)
        self.ambience_thread.start()

    def stop_ambience(self, force=False):
        """
        Stop the current ambience.

        Args:
            force: If True, immediately stop all sounds without playing outro.
                   If False, let the outro play naturally.
        """
        # Signal the ambience thread to stop the loop and play outro
        self.ambience_stop_flag = True

        if force:
            # Forcibly stop all ambience sounds immediately
            if self.ambience_intro:
                try:
                    self.ambience_intro.stop()
                except (AttributeError, OSError, RuntimeError) as exc:
                    LOG.debug("Failed to stop ambience intro: %s", exc)
            if self.ambience_loop:
                try:
                    self.ambience_loop.stop()
                except (AttributeError, OSError, RuntimeError) as exc:
                    LOG.debug("Failed to stop ambience loop: %s", exc)
            if self.ambience_outro:
                try:
                    self.ambience_outro.stop()
                except (AttributeError, OSError, RuntimeError) as exc:
                    LOG.debug("Failed to stop ambience outro: %s", exc)

            self.ambience_intro = None
            self.ambience_loop = None
            self.ambience_outro = None
        # else: Don't forcibly stop sounds - let the thread handle the outro gracefully

    def set_ambience_volume(self, volume):
        """
        Set the ambience volume.

        Args:
            volume: Volume level 0.0-1.0
        """
        self.ambience_volume = max(0.0, min(1.0, volume))

        # Update currently playing ambience sounds
        if self.ambience_intro:
            try:
                self.ambience_intro.volume = self.ambience_volume
            except (AttributeError, OSError, RuntimeError) as exc:
                LOG.debug("Failed to set ambience intro volume: %s", exc)
        if self.ambience_loop:
            try:
                self.ambience_loop.volume = self.ambience_volume
            except (AttributeError, OSError, RuntimeError) as exc:
                LOG.debug("Failed to set ambience loop volume: %s", exc)
        if self.ambience_outro:
            try:
                self.ambience_outro.volume = self.ambience_volume
            except (AttributeError, OSError, RuntimeError) as exc:
                LOG.debug("Failed to set ambience outro volume: %s", exc)

    def add_playlist(
        self,
        playlist_id,
        tracks,
        audio_type="music",
        shuffle=False,
        repeats=1,
        auto_start=True,
        auto_remove=True,
    ):
        """
        Add a new audio playlist.

        Args:
            playlist_id: Unique identifier for this playlist
            tracks: List of audio file names to play
            audio_type: Either "sound" or "music" to determine playback method
            shuffle: If True, shuffle the tracks randomly
            repeats: Number of times to repeat the playlist (0 for infinite, minimum 1 otherwise)
            auto_start: If True, automatically start playing the first track
            auto_remove: If True, automatically remove playlist when all repeats complete (ignored for infinite)
        """
        # Remove existing playlist with same ID if it exists
        if playlist_id in self.playlists:
            self.remove_playlist(playlist_id)

        # Create new playlist
        playlist = AudioPlaylist(
            tracks, audio_type, self, shuffle, repeats, auto_start, auto_remove
        )
        playlist.playlist_id = playlist_id
        self.playlists[playlist_id] = playlist

    def remove_playlist(self, playlist_id):
        """
        Remove and stop a playlist.

        Args:
            playlist_id: Unique identifier of the playlist to remove
        """
        if playlist_id in self.playlists:
            playlist = self.playlists[playlist_id]
            playlist.stop()
            del self.playlists[playlist_id]

    def remove_all_playlists(self):
        """
        Remove and stop all playlists.
        """
        # Create a copy of playlist IDs to iterate over
        playlist_ids = list(self.playlists.keys())
        for playlist_id in playlist_ids:
            self.remove_playlist(playlist_id)

    def get_playlist(self, playlist_id):
        """
        Get a playlist by ID.

        Args:
            playlist_id: Unique identifier of the playlist

        Returns:
            AudioPlaylist object or None if not found
        """
        return self.playlists.get(playlist_id)
