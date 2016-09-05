3200 - Distributed Systems - Fall 2016 - Assignment 1
======================================================

The first assignment is to create a simple distributed hash table. This
repository contains the assignment handouts and some example code to get you
started.

See [`assignment1--key-value-store.pdf`]( assignment1--key-value-store.pdf) for
details on what is expected. The rest of this README focuses on the example
code.

Remember that you are not required to use this example code. You may implement
the project in any language you choose, as long as it uses the same HTTP API.

However you implement the system, be sure to include a README telling us how to
run it. If you reuse this README, don't forget to update it.


# Example Code

The example code is located in the `src/` directory. It consists of three
components (`node.py`, `nameserver.py`, `client.py`) and two helper scripts
(`launch.py`, `rocks_list_random_hosts.sh`). They form the skeleton of a working
system.

## Components

### Nameserver -- `nameserver.py`

`nameserver.py` is the nameserver. It basically works as specified by the
assignment.

    # Start nameserver on port 8000
    cd src/
    ./nameserver.py --port 8000

    # PUT to register a node running on localhost:8010
    curl -X PUT http://localhost:8000/localhost:8010

    # GET to fetch list of nodes
    curl http://localhost:8000

    # Shutdown the server with Ctrl-C or kill (SIGTERM)
    pgrep -f ./nameserver.py | xargs kill

### Node -- `node.py`

`node.py` is the DHT node. The example code merely stores key-value pairs
locally, without talking to any other nodes. Getting the nodes to talk to each
other is up to you. That's the heart of the assignment. Run `node.py -h` for
usage information.

    # Start node on port 8010 and register with nameserver on localhost:8000
    cd src/
    ./node.py --port=8010 --nameserver=localhost:8000

    # PUT a value
    curl -X PUT -d "Hello World!" http://localhost:8010/greeting

    # GET a value
    curl -X GET http://localhost:8010/greeting

    # Shutdown the server with Ctrl-C or kill (SIGTERM)
    pgrep -f ./node.py | xargs kill

### Client -- `client.py`

`client.py` connects to the system and runs a short test, storing and retrieving
some random values.

    # Run tests. Get list of nodes from nameserver at localhost:8000
    ./client.py --nameserver=localhost:8000

As provided, the client's test is very simple and only verifies that the nodes
are storing and serving data. It does not even verify whether the data is
actually distributed.

For the demo, we will run our own client with additional, more thorough tests.
We encourage you to come up with more thorough tests of your own. At the very
minimum, you will have to add code to measure throughput to get the required
throughput graph for your report. Also think about your network design and what
edge cases it might have trouble with. Think about data at different scales, and
the network at different scales. Remember that you can run multiple DHT nodes on
each compute node by using different ports.


## Helper Scripts

### Whole System Launcher -- `launch.py`

`launch.py` launches the whole system in one command. By default, it will wait
until you press enter, and then it will go and kill the servers it launched. The
`--run-tests` option will have it run the client's tests, then clean up.

The launcher script works on both the local machine with various ports, and on
uvrocks with various hosts/ports. Testing is easier locally, but remember that
your project must also run on separate machines on the uvrocks cluster.

    # Launch nameserver localhost:8000, run nodes on localhost:8010, localhost:8011
    # Wait for user to press enter, then clean up
    ./launch.py --nameserver localhost:8000 localhost:8010 localhost:8011

    # Launch nameserver localhost:8000, run nodes on localhost:8010, localhost:8011
    # Run client.py to test the system, then clean up
    ./launch.py --nameserver localhost:8000 localhost:8010 localhost:8011 --run-tests

    # The nameserver is already running on localhost:8000, so just launch nodes
    # on localhost:8010, localhost:8011
    ./nameserver.py --port=8000 &
    ./launch.py --nameserver localhost:8000 --no-launch-nameserver localhost:8010 localhost:8011

    # Launch the system and run tests on various compute nodes of uvrocks
    ./launch.py --nameserver=compute-2-19 compute-1-10 compute-3-32 --run-tests

    # Launch the system and run tests on various compute nodes/ports of uvrocks
    ./launch.py --nameserver=compute-2-19:8000 compute-1-10:8010 compute-3-32:9000 --run-tests

### Cluster Host Randomizer -- `rocks_list_random_hosts.sh`

`rocks_list_random_hosts.sh` selects a number of compute nodes randomly from the
uvrocks cluster. This should make it easier to avoid colliding with other
students on the same node.

    # List 5 random compute node names
    ./rocks_list_random_hosts.sh 5
    compute-3-17 compute-2-11 compute-1-9 compute-2-14 compute-2-22

    # Then copy and paste that list into the launcher command
    ./launch.py --nameserver=compute-3-17 compute-2-11 compute-1-9 compute-2-14 compute-2-22 --run-tests
