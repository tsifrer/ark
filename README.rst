*********************************************
Ark Core implemented in Python
*********************************************

Work in Progress.

If you're new here, and don't know what this is about, `read this`_.


This project will be getting better and better as the time goes on, but please be
patient if something is weird for the time being :)

If you have any questions/suggestions or whatever, find me on Ark Slack @tsifrer.

If you're looking at the code and commits, you might find weird code, messages,
text and other stuff, as this is how I develop and remember things. In the end,
all will be nice and pretty, but untill the basic structure of the project is not
100% complete, whole repo will be a mess.


=============
How to run it
=============

Only for people that like to test new stuff and are happy to report bugs or even fix
them.

This will run relay node against the devnet.

Node is currently set up to run with docker.

- Clone this repo
- :code:`docker-compose build`
- :code:`docker-compose up -d`

For logs blockchain logs, you can run:
:code:`docker-compose logs --tail 50 -f blockchain`

And for p2p-chain (p2p service) logs:
:code:`docker-compose logs --tail 50 -f p2p-chain`

For any other questions, find me on Ark Slack @tsifrer

If you find a bug, open an issue or contact me on Slack.


    Current implementation does NOT broadcast blocks/transactions as it's not yet
    implemented. That will be done after a bit of testing and proper implementation and
    fixes to some of the other features.


.. _read this: https://arkcommunity.fund/proposal/python-port-of-ark-core