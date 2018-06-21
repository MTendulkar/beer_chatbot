
import argparse 
import numpy as np
import tensorflow as tf
import codecs
import pickle 
import time 
import re 
import math 

parser = argparse.ArgumentParser( description='Train from new or restore' )
parser.add_argument( '--last_epoch', action='store', dest='last_epoch', type=int, default=0 )
parser.add_argument( '--num_epochs', action='store', dest='num_epochs', type=int, default=20001 )


## Create lookup tables 
def create_lookup_tables( text ):
    """
    Create lookup tables for vocab
    :param text: The body of text as a string 
    :return: A tuple of dicts (vocab_to_int, int_to_vocab)
    """
    vocab = sorted( set( text) )
    int_to_vocab = {key: word for key, word in enumerate( vocab )}
    vocab_to_int = {word: key for key, word in enumerate( vocab )}

    print("Vocab has {} words".format( len( vocab ) ) )
    return vocab_to_int, int_to_vocab

    # TODO
    # This is very expensive to run. Compute word frequencies; 
    # can be used to filter out uncommon words. 
    #vocab_freq = sorted([(word, text.count(word)) for word in vocab])
    #return vocab_to_int, int_to_vocab, vocab_freq


def token_lookup():
    """
    Generate a dict to map punctuation into a token
    :return: dictionary mapping puncuation to token
    """
    return {
        '.': '||period||',
        ',': '||comma||',
        "''": '||double_quotes||', 
        '"': '||quotes||',
        ';': '||semicolon||',
        '!': '||exclamation_mark||',
        '?': '||question_mark||',
        '(': '||left_parentheses||',
        ')': '||right_parentheses||',
        '--': '||emm_dash||',
        '-': '||dash||',
        '/': '||forward_slash||',
        " '": '||left_quote||',
        "' ": '||right_quote||',
        "||left_quote|| '": '||double_quotes||',
        "' ||right_quote||": '||double_quotes||',
        '\n': '||return||'
    }


def get_batches(int_text, batch_size, seq_length):
    """
    Return batches of input and target data
    :param int_text: text with words replaced by their ids
    :param batch_size: the size that each batch of data should be
    :param seq_length: the length of each sequence
    :return: batches of data as a numpy array
    """
    words_per_batch = batch_size * seq_length
    num_batches = len(int_text)//words_per_batch
    int_text = int_text[:num_batches*words_per_batch]
    y = np.array(int_text[1:] + [int_text[0]])
    x = np.array(int_text)
    
    x_batches = np.split(x.reshape(batch_size, -1), num_batches, axis=1)
    y_batches = np.split(y.reshape(batch_size, -1), num_batches, axis=1)
    
    batch_data = list(zip(x_batches, y_batches))
    
    return np.array(batch_data)

## Import post text

start_time = time.time()

if last_epoch == 0: 
    corpus_raw = u""
    with codecs.open( 'conversationData.txt', 'r', 'utf-8' ) as words: 
        corpus_raw += words.read()

    print("Corpus is {} characters long".format( len( corpus_raw ) ) )

    corpus_raw = re.sub( r'[^\w](")([^\s]*\w)' , r' ||left_double_quote|| \2', corpus_raw )
    corpus_raw = re.sub( r'(\s[^\s]+)(")[^\w]+' , r'\1 ||right_double_quote|| ', corpus_raw )
    corpus_raw = re.sub( r"[^\w](')([^\s]*\w)" , r' ||left_single_quote|| \2', corpus_raw )
    corpus_raw = re.sub( r"(\s[^\s]+)(')[^\w]+" , r'\1 ||right_single_quote|| ', corpus_raw )

    corpus_raw = re.sub( ur"(\w*)(\xe2\x80\x99)(\w*)" , ur"\1'\3", corpus_raw )
    corpus_raw = re.sub( ur"(\w*)(\u201c)(\w*)" , ur'\1"\3', corpus_raw )
    corpus_raw = re.sub( ur"(\w*)(\u201d)(\w*)" , ur'\1"\3', corpus_raw )
    corpus_raw = re.sub( ur"(\w*)(\u2019)(\w*)" , ur"\1'\3", corpus_raw )
    corpus_raw = re.sub( ur"(\w*)(\xe2\x80\x93)(\w*)" , ur"\1-\3", corpus_raw )
    corpus_raw = re.sub( ur"\u2022" , ur"", corpus_raw)

    token_dict = token_lookup()

    for token, replacement in token_dict.items():
        corpus_raw = corpus_raw.replace( token, ' {} '.format( replacement ) )
    #corpus_raw = corpus_raw.lower()
    corpus_raw = corpus_raw.split()

    #vocab_to_int, int_to_vocab, vocab_freq = create_lookup_tables(corpus_raw)
    vocab_to_int, int_to_vocab = create_lookup_tables( corpus_raw )
    corpus_int = [ vocab_to_int[ word ] for word in corpus_raw ]
    pickle.dump( ( corpus_int, vocab_to_int, int_to_vocab, token_dict ), open( 'preprocess.p', 'wb' ) )

else: 
    corpus_int, vocab_to_int, int_to_vocab, token_dict = pickle.load( open( 'preprocess.p', 'rb' ) )

time_elapsed = time.time() - start_time
print( 'time_elapsed for corpus ingestion = {:.3f}'.format( time_elapsed ) )

batch_size = 512
rnn_size = 256
num_layers = 3
keep_prob = 0.9
embed_dim = 256
seq_length = 60
start_learning_rate = 0.0001
save_dir = './save'

start_time = time.time()

with tf.device("/gpu:0"): 
    tf.reset_default_graph()
    train_graph = tf.Graph()
    with train_graph.as_default():    

        # Initialize input placeholders
        input_text = tf.placeholder(tf.int32, [None, None], name='input')
        targets = tf.placeholder(tf.int32, [None, None], name='targets')
        lr = tf.placeholder(tf.float32, name='learning_rate')

        print "Initialization completed"

        # Calculate text attributes
        vocab_size = len(int_to_vocab)
        input_text_shape = tf.shape(input_text)

        print "Text attribute calculations completed"

        # Build the RNN cell
        lstm = tf.contrib.rnn.BasicLSTMCell(num_units=rnn_size)
        drop_cell = tf.contrib.rnn.DropoutWrapper(lstm, output_keep_prob=keep_prob)
        cell = tf.contrib.rnn.MultiRNNCell([drop_cell] * num_layers)

        print "RNN cell built"

        # TODO
        # Set the initial state
        #initial_state = cell.zero_state(input_text_shape[0], tf.float32)
        #initial_state = tf.identity(initial_state, name='initial_state')

        # Random uniform initialization
        state_placeholder = tf.random_normal(shape=(num_layers, 2, batch_size, rnn_size), mean=0.8, stddev=0.1)
        l = tf.unstack(state_placeholder, axis=0)
        initial_state = tuple([tf.nn.rnn_cell.LSTMStateTuple(l[idx][0],l[idx][1]) for idx in range(num_layers)])
        initial_state = tf.identity(initial_state, name='initial_state')

        print "Initial state set" 

        # Create word embedding as input to RNN
        embed = tf.contrib.layers.embed_sequence(input_text, vocab_size, embed_dim, scope='words')

        print "Word embedding created as input to RNN" 

        # Build RNN
        outputs, final_state = tf.nn.dynamic_rnn(cell, embed, dtype=tf.float32)
        final_state = tf.identity(final_state, name='final_state')

        print "RNN built" 

        # Take RNN output and make logits
        # Letting it default to ReLU activation function. 
        logits = tf.contrib.layers.fully_connected(outputs, vocab_size)

        print "Logits built from RNN output" 

        # Calculate the probability of generating each word
        probs = tf.nn.softmax(logits, name='probs')

        print "Word probabilities calculated" 

        # Define loss function
        cost = tf.contrib.seq2seq.sequence_loss(
            logits,
            targets,
            tf.ones([input_text_shape[0], input_text_shape[1]])
        )

        print "Cost function defined" 

        # Learning rate optimizer
        optimizer = tf.train.AdamOptimizer(start_learning_rate)

        # TODO
        # Try different optimizer
        #optimizer = tf.train.AdadeltaOptimizer(learning_rate)

        # Gradient clipping to avoid exploding gradients
        gradients = optimizer.compute_gradients(cost)
        capped_gradients = [(tf.clip_by_value(grad, -1., 1.), var) for grad, var in gradients if grad is not None]
        train_op = optimizer.apply_gradients(capped_gradients)

        time_elapsed = time.time() - start_time
        print('time_elapsed for graph training = {:.3f}'.format(time_elapsed))

last_epoch = 0

pickle.dump((seq_length, save_dir), open('params.p', 'wb'))
batches = get_batches(corpus_int, batch_size, seq_length)
num_batches = len(batches)
start_time = time.time()

print "Process started" 

last_checkpoint_prefix = '/tmp/pretrained.ckpt-' + str(last_epoch)

tf.reset_default_graph()

with tf.Session(graph=train_graph) as sess:
    #session_config=config
    saver = tf.train.Saver(tf.global_variables())
    # If you're loading in a saved model, use the following

    if (last_epoch > 0):
        #saver = tf.train.import_meta_graph(last_checkpoint_prefix + '.meta')
        saver.restore(sess, tf.train.latest_checkpoint('/tmp/'))
        sess.run(tf.local_variables_initializer())
    else: 
        # If you're running a fresh session, use the following
        sess.run(tf.global_variables_initializer())

    epoch_saving_period = 100
    epoch = 0
    state = sess.run(initial_state, {input_text: batches[0][0]})

    for epoch in range(last_epoch,(last_epoch+num_epochs)):
        learning_rate = start_learning_rate / (1.0 + epoch / 1000.0)
        train_loss_sum = 0

        for batch_index, (x, y) in enumerate(batches):
            feed_dict = {
                input_text: x,
                targets: y,
                initial_state: state,
                lr: learning_rate 
            }
            train_loss, state, _ = sess.run([cost, final_state, train_op], feed_dict)

            train_loss_sum = train_loss + train_loss_sum

            time_elapsed = time.time() - start_time

        avg_train_loss = train_loss_sum*1.0 / len(batches)

        print('Epoch {:>3}   avg_train_loss = {:.4f}   time_elapsed = {:.3f}   learning_rate = {}'.format(
                epoch + 1,
                avg_train_loss,
                time_elapsed,
                learning_rate
        ))

        # save model every 10 epochs
        if epoch % epoch_saving_period == 0:
            prior_epoch = epoch - epoch_saving_period 
            savePath = saver.save(sess, "/tmp/pretrained.ckpt", global_step=epoch, write_meta_graph = True)

            print('Model Trained and Saved')

                    

