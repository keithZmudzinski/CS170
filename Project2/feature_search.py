from __future__ import print_function
import pandas as pd
import math, sys

output_string = ''
output_file = open('final_output_small_fwd_28.txt', 'w+')

def get_data():
	data = pd.read_csv('CS170_SMALLtestdata__28.txt', delim_whitespace = True, skipinitialspace=True, header=None)
	print('This dataset has %d features (not including the class attribute), with %d instances.\n' % (data.shape[1] - 1, len(data.index)), file=output_file)
	print('Please wait while I normalize the data...', end = '', file = output_file)
	data = (data - data.mean()) / data.std()
	print(' Done!\n', file = output_file)
	return data

def one_nearest_neighbor(data, features, test_row_index):
	smallest_distance = sys.float_info.max
	smallest_distance_loc = -1
	for i in range(len(data.index)):
		if i == test_row_index:
			continue
		local_distance = 0
		for feature in features:
			local_distance += (data.iat[test_row_index, feature] - data.iat[i, feature]) ** 2
		if local_distance < smallest_distance:
			smallest_distance = local_distance
			smallest_distance_loc = i
	return data.iat[smallest_distance_loc, 0]

def leave_1_out_cross_validation(data, features, best_so_far_accuracy):
	MAX_ALLOWED_INCORRECT = len(data.index) * (1 - best_so_far_accuracy)
	incorrect_so_far = 0

	for i in range(len(data.index)):
		if incorrect_so_far > MAX_ALLOWED_INCORRECT:
			return -1
		correct_class = data.iat[i, 0]
		predicted_class = one_nearest_neighbor(data, features, i)
		# Because comparing floats
		if math.fabs(correct_class - predicted_class) > .01:
			incorrect_so_far += 1
	return (len(data.index) - incorrect_so_far) / float(len(data.index))


def fwd_feature_search(data):
	global output_string
	output_string += 'Beginning search.\n\n'
	current_set_of_features = [] 
	sets_of_features = []
	accuracies = []
	absolute_best_accuracy = 0

	for i in range(1, data.shape[1]):
		feature_to_add_at_this_level = -1
		accuracy_was_improved = False
		best_so_far_accuracy = 0;

		for k in range(1, data.shape[1]):
			if k not in current_set_of_features:
				accuracy = leave_1_out_cross_validation(data, current_set_of_features + [k], best_so_far_accuracy)
				output_features = current_set_of_features[:]
				output_features.append(k)
				output_string += '		Using feature(s) ' + str(output_features) + ' accuracy is %.1f%%\n' % (round(accuracy, 3) * 100)
				if accuracy > best_so_far_accuracy:
					best_so_far_accuracy = accuracy
					feature_to_add_at_this_level = k
				if accuracy > absolute_best_accuracy:
					accuracy_was_improved = True

		accuracies.append(best_so_far_accuracy)
		current_set_of_features.append(feature_to_add_at_this_level)
		absolute_best_accuracy = best_so_far_accuracy if (best_so_far_accuracy > absolute_best_accuracy) else absolute_best_accuracy
		output_string = output_string + '\n\n(Warning, Accuracy has decreased! Continuing search in case of local maxima)' if not(accuracy_was_improved) else output_string
		output_string += '\n\nFeature set ' + str(current_set_of_features) + ' was best, accuracy is %.1f%%\n\n' % (round(best_so_far_accuracy, 3) * 100)
		sets_of_features.append(current_set_of_features[:])
	return sets_of_features, accuracies

def bck_feature_search(data):
	global output_string
	output_string += 'Beginning search.\n\n'
	current_set_of_features = [i for i in range(1, data.shape[1])] 
	sets_of_features = []
	accuracies = []
	absolute_best_accuracy = 0

	for i in range(1, data.shape[1]):
		feature_to_remove_at_this_level = -1
		accuracy_was_improved = False
		best_so_far_accuracy = 0;

		for k in range(1, data.shape[1]):
			if k in current_set_of_features:
				accuracy = leave_1_out_cross_validation(data, current_set_of_features[:k-1] + current_set_of_features[k:], best_so_far_accuracy)
				output_features = current_set_of_features[:]
				output_features.remove(k)
				output_string += '		Using feature(s) ' + str(output_features) + ' accuracy is %.1f%%\n' % (round(accuracy, 3) * 100)
				print('		Using feature(s) ' + str(output_features) + ' accuracy is %.1f%%\n' % (round(accuracy, 3) * 100))
				if accuracy > best_so_far_accuracy:
					best_so_far_accuracy = accuracy
					feature_to_remove_at_this_level = k
				if accuracy > absolute_best_accuracy:
					accuracy_was_improved = True

		accuracies.append(best_so_far_accuracy)
		current_set_of_features.remove(feature_to_remove_at_this_level)
		absolute_best_accuracy = best_so_far_accuracy if (best_so_far_accuracy > absolute_best_accuracy) else absolute_best_accuracy
		output_string = output_string + '\n\n(Warning, Accuracy has decreased! Continuing search in case of local maxima)' if not(accuracy_was_improved) else output_string
		print('\n\nFeature set ' + str(current_set_of_features) + ' was best, accuracy is %.1f%%\n\n' % (round(best_so_far_accuracy, 3) * 100))
		output_string += '\n\nFeature set ' + str(current_set_of_features) + ' was best, accuracy is %.1f%%\n\n' % (round(best_so_far_accuracy, 3) * 100)
		sets_of_features.append(current_set_of_features[:])
	return sets_of_features, accuracies


data = get_data()
features, accuracies = fwd_feature_search(data)
best_accuracy = max(accuracies)
best_features = features[accuracies.index(best_accuracy)]
best_features = '{' + ', '.join([str(feature) for feature in best_features]) + '}'
print('Running nearest neighbor with all %d features, using "leave-one-out" evaluation, I get an accuracy of %.1f%%\n' % (data.shape[1] - 1, round(best_accuracy, 3) * 100), file = output_file)
print(output_string, file = output_file)
print('Finished search!! The best feature subset is %s, which has an accuracy of %.1f%%' % (best_features, round(best_accuracy, 3) * 100), file = output_file)
for feature, accuracy in zip(features, accuracies):
	print('{:>34}, {}'.format(feature, accuracy), file=output_file)
output_file.close()
