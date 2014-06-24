from __future__ import unicode_literals

import logging
import sys

import alsaaudio

from mopidy import mixer

import pykka


logger = logging.getLogger(__name__)


class AlsaMixer(pykka.ThreadingActor, mixer.Mixer):

    def __init__(self, config):
        super(AlsaMixer, self).__init__()
        self.config = config
        self.control = self.config['alsamixer']['control']

        known_controls = alsaaudio.mixers()
        if self.control not in known_controls:
            logger.error(
                'Could not find ALSA mixer control %s. '
                'Known mixers include: %s',
                self.control, ', '.join(known_controls))
            sys.exit(1)

    @property
    def _mixer(self):
        # The mixer must be recreated every time it is used to be able to
        # observe volume/mute changes done by other applications.
        # TODO Use card, device, control from config
        return alsaaudio.Mixer(control=self.control)

    def get_volume(self):
        channels = self._mixer.getvolume()
        if not channels:
            return None
        elif channels.count(channels[0]) == len(channels):
            return int(channels[0])
        else:
            # Not all channels have the same volume
            return None

    def set_volume(self, volume):
        self._mixer.setvolume(volume)
        return True

    def get_mute(self):
        channels_muted = self._mixer.getmute()
        if all(channels_muted):
            return True
        elif not any(channels_muted):
            return False
        else:
            # Not all channels have the same mute state
            return None

    def set_mute(self, muted):
        self._mixer.setmute(int(muted))
        return True
