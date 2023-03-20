import pika
import sys
import json

class Subscriber:
    def __init__(self, queueName, bindingKey, config):
        self.queueName = queueName
        self.bindingKey = bindingKey
        self.config = config
        self.connection = self._create_connection()
        
    def __del__(self):
        self.connection.close()
        
    def _create_connection(self):
        credentials = pika.PlainCredentials('root', 'root')
        parameters=pika.ConnectionParameters(host=self.config['host'],    
        port = self.config['port'], credentials=credentials)
        return pika.BlockingConnection(parameters)
    
    def on_message_callback(self, channel, method, properties, body):
        data = json.loads(body)
        print("Data: {}".format(data['date']))     
        print("Hour: {}".format(data['hour']))      
        print("Brand: {}".format(data['brand']))     
        print("Model: {}".format(data['model']))   
        print("Type: {}".format(data['type']))  
        print("Category: {}".format(data['category']))    
        print("Level: {}".format(data['level']))    
        print('Description: {}'.format(data['description'])) 
        
        binding_key = method.routing_key
        print("received new message for -" + binding_key)
        
    def setup(self):
        channel = self.connection.channel()
        channel.exchange_declare(exchange=self.config['exchange'],
        exchange_type='topic')
        # This method creates or checks a queue
        channel.queue_declare(queue=self.queueName)
        # Binds the queue to the specified exchang
        channel.queue_bind(queue=self.queueName,exchange=self.config['exchange'], routing_key=self.bindingKey)
        channel.basic_consume(queue=self.queueName,
        on_message_callback=self.on_message_callback, auto_ack=True)
        print(' [*] Waiting for data for ' + self.queueName + '. To exit press CTRL+C')
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()
            
config = { 'host': 'localhost', 'port': 5672, 'exchange' : 'topic_logs'}
if len(sys.argv) < 2:
   print('Usage: ' + __file__ + ' <QueueName> <BindingKey>')
   sys.exit()
else:
   queueName = sys.argv[1]
   #key in the form exchange.*
   key = sys.argv[2]
   subscriber = Subscriber(queueName, key, config)
   subscriber.setup()