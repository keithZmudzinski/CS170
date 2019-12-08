import pandas as pd
import math, sys

def get_data(input_data_file):
	data = pd.read_csv(input_data_file, delim_whitespace = True, skipinitialspace=True, header=None)
	print('This dataset has %d features (not including the class attribute), with %d instances.\n' % (data.shape[1] - 1, len(data.index)), file=output_file)
	print('Please wait while I normalize the data...', end = '', file = output_file)
	data = (data - data.mean()) / data.std()
	print(' Done!\n', file = output_file)
	return data

def one_nearest_neighbor(data, features, test_row_index, distances):
	global largest_unadded_feature
	smallest_distance = sys.float_info.max
	smallest_distance_loc = -1
	for i in range(len(data.index)):
		if i == test_row_index:
			continue
		local_distance = 0
		if len(distances) > 0: # Only update running total once per current_set_of_features update
			if len(features) > 1 and smallest_unadded_feature == features[-1]:
				distances[i][test_row_index][0] += distances[i][test_row_index][features[-2]]
			singular_distance = (data.iat[test_row_index, features[-1]] - data.iat[i, features[-1]]) ** 2
			distances[i][test_row_index][features[-1]] = singular_distance
			local_distance = distances[i][test_row_index][0] + singular_distance
		else:
			for feature in features:
				local_distance += (data.iat[test_row_index, feature] - data.iat[i, feature]) ** 2
		if local_distance < smallest_distance:
			smallest_distance = local_distance
			smallest_distance_loc = i
	return data.iat[smallest_distance_loc, 0]

def leave_1_out_cross_validation(data, features, best_so_far_accuracy, distances = []):
	MAX_ALLOWED_INCORRECT = len(data.index) * (1 - best_so_far_accuracy)
	incorrect_so_far = 0

	for i in range(len(data.index)):
		if incorrect_so_far > MAX_ALLOWED_INCORRECT:
			return -1
		correct_class = data.iat[i, 0]
		predicted_class = one_nearest_neighbor(data, features, i, distances)
		# Because comparing floats
		if math.fabs(correct_class - predicted_class) > .01:
			incorrect_so_far += 1
	return (len(data.index) - incorrect_so_far) / float(len(data.index))

def fwd_feature_search(data, isSpecial):
	global output_string
	global smallest_unadded_feature
	distances = []
	if isSpecial:
		distances = [[[0 for k in range(data.shape[1]+ 1)]for i in range(len(data.index))]for n in range(len(data.index))]

	output_string += 'Beginning search.\n\n'
	current_set_of_features = []
	sets_of_features = []
	accuracies = []
	absolute_best_accuracy = 0
	count = 0

	for i in range(1, data.shape[1]):
		feature_to_add_at_this_level = -1
		accuracy_was_improved = False
		best_so_far_accuracy = 0;

		for k in range(1, data.shape[1]):
			if k not in current_set_of_features:
				if isSpecial:
					future_features = set(range(1, data.shape[1])).difference(set(current_set_of_features))
					smallest_unadded_feature = min(future_features)
				accuracy = leave_1_out_cross_validation(data, current_set_of_features + [k], best_so_far_accuracy, distances)
				output_features = current_set_of_features[:]
				output_features.append(k)
				output_string += '		Using feature(s) ' + str(output_features) + ' accuracy is %.1f%%\n' % (round(accuracy, 3) * 100)
				if accuracy > best_so_far_accuracy:
					best_so_far_accuracy = accuracy
					feature_to_add_at_this_level = k
				if accuracy > absolute_best_accuracy:
					accuracy_was_improved = True
					count = 0
		if not(accuracy_was_improved):
			count += 1
		accuracies.append(best_so_far_accuracy)
		current_set_of_features.append(feature_to_add_at_this_level)
		absolute_best_accuracy = best_so_far_accuracy if (best_so_far_accuracy > absolute_best_accuracy) else absolute_best_accuracy
		output_string = output_string + '\n\n(Warning, Accuracy has decreased! Continuing search in case of local maxima)' if not(accuracy_was_improved) else output_string
		output_string += '\n\nFeature set ' + str(current_set_of_features) + ' was best, accuracy is %.1f%%\n\n' % (round(best_so_far_accuracy, 3) * 100)
		sets_of_features.append(current_set_of_features[:])
		if count >= 2:
			break
	return sets_of_features, accuracies

def bck_feature_search(data, ignore):
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
				if accuracy > best_so_far_accuracy:
					best_so_far_accuracy = accuracy
					feature_to_remove_at_this_level = k
				if accuracy > absolute_best_accuracy:
					accuracy_was_improved = True

		accuracies.append(best_so_far_accuracy)
		current_set_of_features.remove(feature_to_remove_at_this_level)
		absolute_best_accuracy = best_so_far_accuracy if (best_so_far_accuracy > absolute_best_accuracy) else absolute_best_accuracy
		output_string = output_string + '\n\n(Warning, Accuracy has decreased! Continuing search in case of local maxima)' if not(accuracy_was_improved) else output_string
		output_string += '\n\nFeature set ' + str(current_set_of_features) + ' was best, accuracy is %.1f%%\n\n' % (round(best_so_far_accuracy, 3) * 100)
		sets_of_features.append(current_set_of_features[:])
	return sets_of_features, accuracies


output_string = ''
smallest_unadded_feature = -1

print('Welcome to Keith Zmudzinski\'s Feature Selection Algorithm.')
print('Type in the name of the file to test: ', end = '')

input_data_file = input()

print('\nType the number of the algorithm you want to run.\n')
print('''		1) Forward Selection
		2) Backward Elimination
		3) Keith's Special Algorithm\n''')

choice = input()
feature_selection = bck_feature_search if choice == '2' else fwd_feature_search
isSpecial = True if choice == '3' else False

data = get_data(input_data_file)
features, accuracies = feature_selection(data, isSpecial)
best_accuracy = max(accuracies)
best_features = features[accuracies.index(best_accuracy)]
best_features = '{' + ', '.join([str(feature) for feature in best_features]) + '}'

print('Running nearest neighbor with all %d features, using "leave-one-out" evaluation, I get an accuracy of %.1f%%\n' % (data.shape[1] - 1, round(best_accuracy, 3) * 100))
print(output_string)
print('Finished search!! The best feature subset is %s, which has an accuracy of %.1f%%' % (best_features, round(best_accuracy, 3) * 100))
