*UNFINISHED and NOT MAINTAINED*

*********************************************
ARK Blockchain implemented in Python
*********************************************

.. image:: https://circleci.com/gh/tsifrer/ark.svg?style=svg
    :target: https://circleci.com/gh/tsifrer/ark
    



=============
How to run it
=============

Only for people that like to test new stuff and are happy to report bugs or even fix
them.

This will run relay node against the devnet.

Node is currently set up to run with docker.

- Clone this repo
- :code:`make build`
- :code:`make start`

For logs blockchain logs, you can run:
:code:`make blockchain-logs`

For chain-p2p (p2p service) logs:
:code:`make p2p-logs`

For chain-huey (huey service for running async tasks) logs:
:code:`make huey-logs`

    Current implementation does NOT broadcast blocks/transactions as it's not yet
    implemented. That will be done after a bit of testing and proper implementation and
    fixes to some of the other features.
