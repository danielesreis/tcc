import cv2
import math
import numpy as np
import pandas as pd
from MNGFeaturesSize import MNGFeaturesSize
from MNGFeaturesMeans import MNGFeaturesMeans
from MNGFeaturesDominantColor import MNGFeaturesDominantColor
from MNGFeaturesRates import MNGFeaturesRates
from MNGFeaturesGradient import MNGFeaturesGradient
from MNGFeaturesFractal import MNGFeaturesFractal
from MNGFeaturesRegions import MNGFeaturesRegions

class MNGFeatures():

	feature_names	= [ 'mean_R_full', 'mean_G_full', 'mean_B_full',															\
						'mean_H_full', 'mean_S_full', 'mean_V_full',															\
						'mean_L_full', 'mean_a_full', 'mean_b_full',															\
						'area', 'diameter',																						\
						'dominant_HSV',																							\
						'RG_rate', 'RB_rate', 'SH_rate',																		\
						'long_gradient',																						\
						'bcd', 'cd', 'dd',																						\
						'RG_diff_full', 'RB_diff_full', 'GB_diff_full',																		\
						'apex_R', 'apex_G', 'apex_B', 'equator_R', 'equator_G', 'equator_B', 'stalk_R', 'stalk_G', 'stalk_B',	\
						'apex_equator_R_diff', 'equator_stalk_R_diff', 'apex_stalk_R_diff', 									\
						'apex_equator_G_diff', 'equator_stalk_G_diff', 'apex_stalk_G_diff',										\
						'apex_equator_B_diff', 'equator_stalk_B_diff', 'apex_stalk_B_diff']										\

	def new_df(self):
		self.data = pd.DataFrame(index=self.image_names, columns=self.current_features)

	def insert_feature_row(self, img_name, feature_values):
		feature_row = pd.Series(data=feature_values, index=self.current_features, name=img_name.split('.')[0])
		self.data.loc[img_name.split('.')[0]] = feature_row

	def save_data(self):
		file_path = self.dest_folder + self.current_features_name + '_all.csv'
		self.data.to_csv(file_path, sep=';')
		return file_path

	def edit_feature_names(self):
		names_means = self.features_regions.get_var_mean_names()
		names_diffs = self.features_regions.get_var_mean_diffs_names()

		names = [names_means, names_diffs]
		names = [item for sublist in names for item in sublist]

		self.feature_names = [self.feature_names, names]
		self.feature_names = [item for sublist in self.feature_names for item in sublist]

	@property
	def current_features(self):
		return self._current_features

	@current_features.setter
	def current_features(self, current_features):
		self._current_features = current_features

	@property
	def current_features_name(self):
		return self._current_features_name

	@current_features_name.setter
	def current_features_name(self, current_features_name):
		self._current_features_name = current_features_name
	

	# def get_feature_method(features):
	# 	indexes = list()

	# 	for index,name in enumerate(self.feature_names):
	# 		if name in self.current_features:
	# 			indexes.append(index)

	# 	methods = [self.feature_methods[index] for index in indexes]
	# 	return methods

	def __init__(self, folder, image_names):
		self.dest_folder 		= folder + '..\\features\\'
		self.image_names		= [image_name.split('.')[0] for image_name in image_names]

		self.features_means		= MNGFeaturesMeans()
		self.features_size 		= MNGFeaturesSize()
		self.features_dominant	= MNGFeaturesDominantColor(self.features_means)
		self.features_rates		= MNGFeaturesRates(self.features_means)
		self.features_gradient	= MNGFeaturesGradient()
		self.features_regions	= MNGFeaturesRegions(self.features_means)
		self.features_fractal	= MNGFeaturesFractal()

		self._current_features  	= None
		self._current_features_name = None
		self.data 					= None
		self.edit_feature_names()

	def extract_features(self, BGR_img, img_name):
		gray_img = cv2.cvtColor(BGR_img, cv2.COLOR_BGR2GRAY)
		
		RGB_img = BGR_img[:,:,::-1]
		HSV_img = cv2.cvtColor(RGB_img, cv2.COLOR_RGB2HSV)
		Lab_img = cv2.cvtColor(RGB_img, cv2.COLOR_RGB2Lab)

		if self.current_features == self.feature_names[:9]:
			means_RGB 				= self.features_means.channels_mean(RGB_img)
			means_HSV 				= self.features_means.channels_mean(HSV_img)
			means_Lab 				= self.features_means.channels_mean(Lab_img)

			feature_values = list(np.concatenate((means_RGB, means_HSV, means_Lab), axis=None))

		elif self.current_features == self.feature_names[9:11]:
			area					= self.features_sizes.estimated_area(gray_img)
			diameter				= self.features_sizes.estimated_diameter(gray_img)

			feature_values = [area, diameter]

		elif self.current_features == self.feature_names[11:12]:
			dominant_HSV		  	= self.features_dominant.dominant_HSV_color(HSV_img)

			feature_values = dominant_HSV

		elif self.current_features == self.feature_names[12:14]:
			rates_RGB		 		= self.features_rates.space_rates(RGB_img)
			rates_HSV				= self.features_rates.space_rates(HSV_img)

			feature_values = [rates_RGB[0], rates_RGB[1], rates_HSV[0]]

		elif self.current_features == self.feature_names[11:12]:
			long_gradient			= self.features_gradient.longitudinal_gradient(RGB_img)

			feature_values = long_gradient

		elif self.current_features == self.feature_names[12:15]:
			bcd		  	 			= self.features_fractal.box_counting_dimension(gray_img)
			cd		  				= self.features_fractal.correlation_dimension(gray_img)
			dd		  				= self.features_fractal.dilation_dimension(gray_img)

			feature_values = [bcd, cd, dd]

		elif self.current_features == self.feature_names[15:18]:
			means_diffs_full 					= self.features_regions.mean_diffs(RGB_img, 1)
			means_apex_equator_stalk 			= self.features_regions.apex_equator_stalk_means(img)
			mean_diffs_apex_equator_stalk_RGB	= self.features_regions.regions_means_diffs(RGB_img)

			feature_values = list(np.concatenate((means_diffs_full.flatten(), means_apex_equator_stalk.flatten(), mean_diffs_apex_equator_stalk_RGB.flatten()), axis=None))

		elif self.current_features == self.feature_names[18:24]:
			means_n_RGB				= self.features_regions.regions_means(RGB_img, n)
			means_n_HSV				= self.features_regions.regions_means(HSV_img, n)
			means_n_Lab				= self.features_regions.regions_means(Lab_img, n)
			means_diffs_n_RGB		= self.features_regions.mean_diffs(RGB_img, n)
			means_diffs_n_HSV		= self.features_regions.mean_diffs(HSV_img, n)
			means_diffs_n_Lab		= self.features_regions.mean_diffs(Lab_img, n)

			feature_values = list(np.concatenate((means_n_RGB.flatten(), means_n_HSV.flatten(), means_n_Lab.flatten(), means_diffs_n_RGB.flatten(), means_diffs_n_HSV.flatten(), means_diffs_n_Lab.flatten()), axis=None))
			
		elif self.current_features == self.feature_names:
			means_RGB 				= self.features_means.channels_mean(RGB_img)
			means_HSV 				= self.features_means.channels_mean(HSV_img)
			means_Lab 				= self.features_means.channels_mean(Lab_img)

			area					= self.features_sizes.estimated_area(gray_img)
			diameter				= self.features_sizes.estimated_diameter(gray_img)

			dominant_HSV		  	= self.features_dominant.dominant_HSV_color(HSV_img)

			rates_RGB		 		= self.features_rates.space_rates(RGB_img)
			rates_HSV				= self.features_rates.space_rates(HSV_img)

			long_gradient			= self.features_gradient.longitudinal_gradient(RGB_img)

			bcd		  	 			= self.features_fractal.box_counting_dimension(gray_img)
			cd		  				= self.features_fractal.correlation_dimension(gray_img)
			dd		  				= self.features_fractal.dilation_dimension(gray_img)

			means_diffs_full 					= self.features_regions.mean_diffs(RGB_img, 1)
			means_apex_equator_stalk 			= self.features_regions.apex_equator_stalk_means(img)
			mean_diffs_apex_equator_stalk_RGB	= self.features_regions.regions_means_diffs(RGB_img)

			means_n_RGB				= self.features_regions.regions_means(RGB_img, n)
			means_n_HSV				= self.features_regions.regions_means(HSV_img, n)
			means_n_Lab				= self.features_regions.regions_means(Lab_img, n)
			means_diffs_n_RGB		= self.features_regions.mean_diffs(RGB_img, n)
			means_diffs_n_HSV		= self.features_regions.mean_diffs(HSV_img, n)
			means_diffs_n_Lab		= self.features_regions.mean_diffs(Lab_img, n)

			feature_values = list(np.concatenate((	means_RGB, means_HSV, means_Lab, 																				\
													[area], [diameter], 																							\
													[dominant_HSV], 																								\
													[rates_RGB[0]], [rates_RGB[1]], [rates_HSV[0]], 																\
													[long_gradient], 																								\
													[bcd], [cd], [dd], 																								\
													means_diffs_full.flatten(), means_apex_equator_stalk.flatten(), mean_diffs_apex_equator_stalk_RGB.flatten(), 	\
													means_n_RGB.flatten(), means_n_HSV.flatten(), means_n_Lab.flatten(),means_diffs_n_RGB.flatten(), 				\
													means_diffs_n_HSV.flatten(), means_diffs_n_Lab.flatten()), axis=None))		

		self.insert_feature_row(img_name, feature_values)
