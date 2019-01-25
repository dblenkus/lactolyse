from django.conf.urls import url

from channels.routing import ChannelNameRouter, ProtocolTypeRouter, URLRouter
from channels.sessions import SessionMiddlewareStack

from lactolyse.consumers import ClientConsumer, RunAnalysisConsumer
from lactolyse.protocol import RUN_ANALYSIS_CHANNEL


application = ProtocolTypeRouter(
    {
        # Client-facing consumers.
        'websocket': SessionMiddlewareStack(URLRouter([url(r'^ws/$', ClientConsumer)])),
        # Background worker consumers.
        'channel': ChannelNameRouter({RUN_ANALYSIS_CHANNEL: RunAnalysisConsumer}),
    }
)
