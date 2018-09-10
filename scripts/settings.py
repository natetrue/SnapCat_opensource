
# settings for retrain script
retrain = dict(
    image_dir = './training/processed_images/',
    output_graph = './output_graphs/output_graph.pb',
    intermediate_output_graphs_dir = './output_graphs/intermediate_outputs/',
    intermediate_store_frequency = 100,
    output_labels = './scripts/labels.txt',
    summaries_dir = './retrain_logs',
    how_many_training_steps = 500,
    learning_rate = 0.0001,
    testing_percentage = 20,
    validation_percentage = 20,
    eval_step_interval = 100,
    train_batch_size = 32,
    test_batch_size = -1,
    validation_batch_size = -1,
    print_misclassified_test_images = False,
    bottleneck_dir = './bottleneck',
    final_tensor_name = 'final_result',
    flip_left_right = False,
    random_crop = 30,
    random_scale = 30,
    random_brightness = 30,
    tfhub_module = "https://tfhub.dev/google/imagenet/mobilenet_v2_140_224/feature_vector/1",
    saved_model_dir = ''
)