"""
███████╗███╗   ██╗ █████╗ ██████╗  ██████╗ █████╗ ████████╗
██╔════╝████╗  ██║██╔══██╗██╔══██╗██╔════╝██╔══██╗╚══██╔══╝
███████╗██╔██╗ ██║███████║██████╔╝██║     ███████║   ██║   
╚════██║██║╚██╗██║██╔══██║██╔═══╝ ██║     ██╔══██║   ██║   
███████║██║ ╚████║██║  ██║██║     ╚██████╗██║  ██║   ██║   
╚══════╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝      ╚═════╝╚═╝  ╚═╝   ╚═╝                  
"""
# settings for retrain script
retrain = dict(
    image_dir = './training/processed_images/',
    output_graph = './output_graphs/output_graph.pb',
    intermediate_output_graphs_dir = './output_graphs/intermediate_outputs/',
    intermediate_store_frequency = 100,
    output_labels = './scripts/labels.txt',
    summaries_dir = './tmp/retrain_logs',
    how_many_training_steps = 500,
    learning_rate = 0.0001,
    testing_percentage = 20,
    validation_percentage = 20,
    eval_step_interval = 100,
    train_batch_size = 32,
    test_batch_size = -1,
    validation_batch_size = -1,
    print_misclassified_test_images = False,
    bottleneck_dir = './tmp/bottleneck',
    final_tensor_name = 'final_result',
    flip_left_right = False,
    random_crop = 30,
    random_scale = 30,
    random_brightness = 30,
    tfhub_module = "https://tfhub.dev/google/imagenet/mobilenet_v2_140_224/feature_vector/1",
    saved_model_dir = ''
)

# settings for the graph
graph = dict(
    graph = './output_graphs/output_graph.pb',
    labels = './scripts/labels.txt',
    input_height = 224,
    input_width = 224,
    input_mean = 0,
    input_std = 255,
    input_layer = 'module_apply_default/MobilenetV2/input',
    output_layer = 'final_result',
)

# settings for label_image script
label_image = dict(
	cat_directory = './testing/processed_images/cats/',
	NC_directory = './testing/processed_images/not_cats/',
)

# settings for sort_image script
sort_image = dict(
    confidence_threshold = .65
)

#settings for segmentation script
segmentation = dict(
    diff_threshold = .6,
    min_square_size = 100
)

# settings for burst.py
burst = dict(
    img_buffer = 300,
    burst_threshold = 3600
)