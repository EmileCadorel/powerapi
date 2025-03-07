# Copyright (c) 2018, INRIA
# Copyright (c) 2018, University of Lille
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import logging
from powerapi.actor import Actor, State, SocketInterface
from powerapi.pusher import ReportHandler, PusherStartHandler, PusherPoisonPillMessageHandler
from powerapi.message import PoisonPillMessage, StartMessage

class PusherState(State):
    """
    Pusher Actor State

    Contains in addition to State values :
      - The database interface
    """
    def __init__(self, actor, database, report_model, asynchrone = False):
        """
        :param BaseDB database: Database for saving data.
        """
        State.__init__(self, actor)

        #: (BaseDB): Database for saving data.
        self.database = database

        #: (Report): Type of the report that the pusher handle.
        self.report_model = report_model

        #: (Dict): Buffer data.
        self.buffer = []

        self.asynchrone = asynchrone


class PusherActor(Actor):
    """
    PusherActor class

    The Pusher allow to save Report sent by Formula.
    """

    def __init__(self, name, report_model, database, level_logger=logging.WARNING, timeout=1000, delay=100, max_size=50):
        """
        :param str name: Pusher name.
        :param Report report_model: ReportModel
        :param BaseDB database: Database use for saving data.
        :param int level_logger: Define the level of the logger
        :param int delay: number of ms before message containing in the buffer will be writen in database
        :param int max_size: maximum of message that the buffer can store before write them in database
        """
        Actor.__init__(self, name, level_logger, timeout)

        #: (State): State of the actor.
        self.state = PusherState(self, database, report_model, asynchrone=database.asynchrone)
        self.delay = delay
        self.max_size = max_size

    def setup(self):
        """
        Define StartMessage, PoisonPillMessage handlers and a handler for
        each report type
        """
        self.add_handler(PoisonPillMessage, PusherPoisonPillMessageHandler(self.state))
        self.add_handler(self.state.report_model.get_type(), ReportHandler(self.state, self.delay, self.max_size))
        self.add_handler(StartMessage, PusherStartHandler(self.state))
