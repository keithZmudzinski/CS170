import pandas as pd
import random, math, copy, numpy
import sys

def get_data():
	data = pd.read_csv('CS170_SMALLtestdata__1.txt', delim_whitespace = True, skipinitialspace=True, header=None)
	# saved_classes = data.iloc[:, 0].copy()
	# print('Initial untouched  data:\n', data)
	# means = data.apply(numpy.mean)
	# # print('Data after numpy.mean applied:\n', means)
	# std_deviations = data.apply(numpy.std)
	# # print('Data after numpy.std applied:\n', std_deviations)
	# data = data.apply(lambda x : (x - means) / std_deviations)
	# sys.exit(1)
	data = (data - data.mean()) / data.std()
	# data.iloc[:, 0] = saved_classes
	print(data)
	return data

def calc_distance(row, features, test_row):
	sum = 0
	for feature in features:
		sum += (row.iloc[feature] - test_row.iloc[feature]) ** 2
	return sum

def one_nearest_neighbor(data, features, test_row_index):
	# distances = data.apply(calc_distance, axis = 1, args = [features, data.iloc[test_row_index]])
	# distances =  distances.drop(test_row_index)
	# smallest_distance = sys.float_info.max
	# index = -1
	# for i, distance in enumerate(distances):
	# 	if distance < smallest_distance:
	# 		smallest_distance = distance
	# 		index = i
	# # sys.exit(1)
	# return data.iat[index, 0]
    smallest_distance = sys.float_info.max
    guessed_class_index = -1
    for i in range(len(data.index)):
        sum = 0
        for feature in features:
            temp1 = data.iat[i, feature]
            temp2 = data.iat[test_row_index, feature]
            # print(temp2)
            sum += (temp1 - temp2) ** 2
        curr_dist = sum
        # print(curr_dist)
        if curr_dist < smallest_distance and i != test_row_index:
            smallest_distance = curr_dist
            guessed_class_index = i
    # print(smallest_distance, curr_dist)
    return data.iat[guessed_class_index, 0]



def leave_1_out_cross_validation(data, current_set, feature_to_add, best_so_far_accuracy):
	MAX_ALLOWED_INCORRECT = len(data.index) * (1 - best_so_far_accuracy)
	incorrect_so_far = 0

	for i in range(len(data.index)):
		if incorrect_so_far > MAX_ALLOWED_INCORRECT:
			# print('speed up worked, %d incorrect' % incorrect_so_far)
			return -1
		correct_class = data.iat[i, 0]
		predicted_class = one_nearest_neighbor(data, current_set + [feature_to_add], i)
		# Because comparing floats
		if math.fabs(correct_class - predicted_class) > .001:
			incorrect_so_far += 1
	return (len(data.index) - incorrect_so_far) / float(len(data.index))


def feature_search(data):
	current_set_of_features = []
	sets_of_features = []
	accuracies = []

	for i in range(1, data.shape[1]):
		print('On the %dth level of the search tree' % i)
		feature_to_add_at_this_level = -1
		best_so_far_accuracy = 0;
		accuracy_was_improved = False

		for k in range(1, data.shape[1]):
			if k not in current_set_of_features:
				print('--Considering adding the %dth feature' % k)
				accuracy = leave_1_out_cross_validation(data, current_set_of_features, k, best_so_far_accuracy)
				# print('accuracy with %dth feature: %f' % (k, accuracy))
				if accuracy > best_so_far_accuracy:
					print('Accuracy improved from %f to %f' % (best_so_far_accuracy, accuracy))
					best_so_far_accuracy = accuracy
					feature_to_add_at_this_level = k
		accuracies.append(copy.copy(best_so_far_accuracy))
		current_set_of_features.append(feature_to_add_at_this_level)
		sets_of_features.append(current_set_of_features[:])
		print('On level %d I added feature %d to current set; current features are %s\n' % (i, feature_to_add_at_this_level, str(current_set_of_features)))

	return sets_of_features, accuracies

if __name__ == '__main__':
	data = get_data()
	# print(data)
	features, accuracies = feature_search(data)
	for feature, accuracy in zip(features, accuracies):
		print(feature, accuracy)
