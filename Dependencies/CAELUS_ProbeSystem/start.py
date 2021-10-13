from ProbeSystem.probes.echo_subscriber import EchoSubscriber
from ProbeSystem.state_aggregator.state_aggregator import StateAggregator
from ProbeSystem.helper_data.subscriber import Subscriber

def run(drone_instance_id, subscribers):
    aggregator = StateAggregator(drone_instance_id)
    for stream_id, subscriber in subscribers:
        aggregator.subscribe(stream_id, subscriber)
    aggregator.report_subscribers()
    aggregator.idle()

def get_all_subscribers():
    from automatic_probe_import import import_all_probes
    subscribers = []
    for subscriber in import_all_probes(base_class=Subscriber):
        sub_streams = subscriber.subscribes_to_streams()
        for stream_id in sub_streams:
            subscribers.append((stream_id, subscriber))
    return subscribers

if __name__ == '__main__':
    drone_instance_id = 'test_drone'
    subscribers = get_all_subscribers()
    run(drone_instance_id, subscribers)

