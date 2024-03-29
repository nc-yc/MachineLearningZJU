import numpy as np


class DecisionTree:
    '''Decision Tree Classifier.

    Note that this class only supports binary classification.
    '''

    def __init__(self,
                 criterion,
                 max_depth,
                 min_samples_leaf,
                 sample_feature=False):
        '''Initialize the classifier.

        Args:
            criterion (str): the criterion used to select features and split nodes.
            max_depth (int): the max depth for the decision tree. This parameter is
                a trade-off between underfitting and overfitting.
            min_samples_leaf (int): the minimal samples in a leaf. This parameter is a trade-off
                between underfitting and overfitting.
            sample_feature (bool): whether to sample features for each splitting. Note that for random forest,
                we would randomly select a subset of features for learning. Here we select sqrt(p) features.
                For single decision tree, we do not sample features.
        '''
        if criterion == 'infogain_ratio':
            self.criterion = self._information_gain_ratio
        elif criterion == 'entropy':
            self.criterion = self._information_gain
        elif criterion == 'gini':
            self.criterion = self._gini_purification
        else:
            raise Exception('Criterion should be infogain_ratio or entropy or gini')
        self._tree = None
        self.max_depth = max_depth
        self.min_samples_leaf = min_samples_leaf
        self.sample_feature = sample_feature#no

    def fit(self, X, y, sample_weights=None):
        """Build the decision tree according to the training data.

        Args:
            X: (pd.Dataframe) training features, of shape (N, D). Each X[i] is a training sample.
            y: (pd.Series) vector of training labels, of shape (N,). y[i] is the label for X[i], and each y[i] is
            an integer in the range 0 <= y[i] <= C. Here C = 1.
            sample_weights: weights for each samples, of shape (N,).
        """
        if sample_weights is None:
            # if the sample weights is not provided, then by default all
            # the samples have unit weights.
            sample_weights = np.ones(X.shape[0]) / X.shape[0]
        else:
            sample_weights = np.array(sample_weights) / np.sum(sample_weights)
            
        if self.sample_feature:
            col=X.columns.tolist()
            import random
            random.shuffle(col)
            X=X[col[:int(len(col)**0.5)]]
        
        feature_names = X.columns.tolist()
        X = np.array(X)
        y = np.array(y)
        self._tree = self._build_tree(X, y, feature_names, depth=1, sample_weights=sample_weights)
        return self

    @staticmethod
    def entropy(y, sample_weights):
        """Calculate the entropy for label.

        Args:
            y: vector of training labels, of shape (N,).
            sample_weights: weights for each samples, of shape (N,).

        Returns:
            (float): the entropy for y.
        """
        entropy = 0.0
        # begin answer
        P0=np.sum(1-y)/y.shape[0]
        P1=np.sum(y)/y.shape[0]
        if not P0:lg0=0
        else: lg0=np.log2(P0)
        if not P1:lg1=0
        else: lg1=np.log2(P1)
        entropy=-P0*lg0-P1*lg1
        # end answer
        return entropy

    def _information_gain(self, X, y, index, sample_weights):
        """Calculate the information gain given a vector of features.

        Args:
            X: training features, of shape (N, D).
            y: vector of training labels, of shape (N,).
            index: the index of the feature for calculating. 0 <= index < D
            sample_weights: weights for each samples, of shape (N,).

        Returns:
            (float): the information gain calculated.
        """
        info_gain = 0
        # YOUR CODE HERE
        # begin answer
        sum_Ent=0
        features=np.unique(X[:,index])
        for i in features:
            sub_X, sub_y, sub_sample_weights=self._split_dataset(X, y, index, i, sample_weights)
            sum_Ent+=self.entropy(sub_y,sub_sample_weights)*np.sum(X[:,index]==i)/X[:,index].shape[0]
        info_gain=self.entropy(y,sample_weights)-sum_Ent
        # end answer
        return info_gain

    def _information_gain_ratio(self, X, y, index, sample_weights):
        """Calculate the information gain ratio given a vector of features.
        Args:
            X: training features, of shape (N, D).
            y: vector of training labels, of shape (N,).
            index: the index of the feature for calculating. 0 <= index < D
            sample_weights: weights for each samples, of shape (N,).

        Returns:
            (float): the information gain ratio calculated.
        """
        info_gain_ratio = 0
        split_information = 0.0
        # YOUR CODE HERE
        # begin answer
        values=np.unique(X[:,index])
        for v in values:
            P=np.sum(X[:,index]==v)/X[:,index].shape[0]
            if P!=0:lg=np.log2(P)
            else:lg=0
            split_information-=P*lg
        info_gain_ratio=self._information_gain(X,y,index,sample_weights)/split_information
        # end answer
        return info_gain_ratio

    @staticmethod
    def gini_impurity(y, sample_weights):
        """Calculate the gini impurity for labels.

        Args:
            y: vector of training labels, of shape (N,).
            sample_weights: weights for each samples, of shape (N,).

        Returns:
            (float): the gini impurity for y.
        """
        gini = 1
        # YOUR CODE HERE
        # begin answer
        values=np.unique(y)
        for v in values:
            gini-=(np.sum(y==v)/y.shape[0])**2
        # end answer
        return gini

    def _gini_purification(self, X, y, index, sample_weights):
        """Calculate the resulted gini impurity given a vector of features.

        Args:
            X: training features, of shape (N, D).
            y: vector of training labels, of shape (N,).
            index: the index of the feature for calculating. 0 <= index < D
            sample_weights: weights for each samples, of shape (N,).

        Returns:
            (float): the resulted gini impurity after splitting by this feature.
        """
        new_impurity = 0
        # YOUR CODE HERE
        # begin answer
        values=np.unique(X[:,index])
        for v in values:
            sub_X, sub_y, sub_sample_weights=self._split_dataset(X, y, index, v, sample_weights)
            new_impurity+=np.sum(X[:,index]==v)/X.shape[0]*self.gini_impurity(sub_y,sub_sample_weights)
        # end answer
        return new_impurity

    def _split_dataset(self, X, y, index, value, sample_weights):
        """Return the split of data whose index-th feature equals value.

        Args:
            X: training features, of shape (N, D).
            y: vector of training labels, of shape (N,).
            index: the index of the feature for splitting.
            value: the value of the index-th feature for splitting.
            sample_weights: weights for each samples, of shape (N,).

        Returns:
            (np.array): the subset of X whose index-th feature equals value.
            (np.array): the subset of y whose index-th feature equals value.
            (np.array): the subset of sample weights whose index-th feature equals value.
        """
        sub_X, sub_y, sub_sample_weights = X, y, sample_weights
        # YOUR CODE HERE
        # Hint: Do not forget to remove the index-th feature from X.
        # begin answer
        feature=X[:,index]
        X = np.delete(X, index, axis=1)
        sub_X=X[feature==value,:]
        sub_y=y[feature==value]
        sub_sample_weights=sample_weights[feature==value]
        # end answer
        return sub_X, sub_y, sub_sample_weights

    def _choose_best_feature(self, X, y, sample_weights):
        """Choose the best feature to split according to criterion.

        Args:
            X: training features, of shape (N, D).
            y: vector of training labels, of shape (N,).
            sample_weights: weights for each samples, of shape (N,).

        Returns:
            (int): the index for the best feature
        """
        best_feature_idx = 0
        # YOUR CODE HERE
        # Note that you need to implement the sampling feature part here for random forest!
        # Hint: You may find `np.random.choice` is useful for sampling.
        # begin answer
        if self.criterion!=self._gini_purification:
            for i in range(X.shape[1]):
                if(self.criterion(X,y,i,sample_weights)>self.criterion(X,y,best_feature_idx,sample_weights)):
                    best_feature_idx=i
        else:
            for i in range(X.shape[1]):
                if(self.criterion(X,y,i,sample_weights)<self.criterion(X,y,best_feature_idx,sample_weights)):
                    best_feature_idx=i
            

        # end answer
        return best_feature_idx

    @staticmethod
    def majority_vote(y, sample_weights=None):
        """Return the label which appears the most in y.

        Args:
            y: vector of training labels, of shape (N,).
            sample_weights: weights for each samples, of shape (N,).

        Returns:
            (int): the majority label
        """
        if sample_weights is None:
            sample_weights = np.ones(y.shape[0]) / y.shape[0]
        majority_label = y[0]
        # YOUR CODE HERE
        # begin answer
        y=list(y)
        majority_label = max(set(y), key=y.count)
        # end answer
        return majority_label

    def _build_tree(self, X, y, feature_names, depth, sample_weights):
        """Build the decision tree according to the data.

        Args:
            X: (np.array) training features, of shape (N, D).
            y: (np.array) vector of training labels, of shape (N,).
            feature_names (list): record the name of features in X in the original dataset.
            depth (int): current depth for this node.
            sample_weights: weights for each samples, of shape (N,).

        Returns:
            (dict): a dict denoting the decision tree. 
            Example:
                The first best feature name is 'title', and it has 5 different values: 0,1,2,3,4. For 'title' == 4, the next best feature name is 'pclass', we continue split the remain data. If it comes to the leaf, we use the majority_label by calling majority_vote.
                mytree = {
            'titile': {
                        0: subtree0,
                        1: subtree1,
                        2: subtree2,
                        3: subtree3,
                        4: {
                            'pclass': {
                                1: majority_vote([1, 1, 1, 1]) # which is 1, majority_label
                                2: majority_vote([1, 0, 1, 1]) # which is 1
                                3: majority_vote([0, 0, 0]) # which is 0
                            }
                        }
                    }
                }
        """
        mytree = dict()
        # YOUR CODE HERE
        # TODO: Use `_choose_best_feature` to find the best feature to split the X. Then use `_split_dataset` to
        # get subtrees.
        # Hint: You may find `np.unique` is useful. build_tree is recursive.
        # begin answer
        
        
        # stop build decision tree
        if depth==self.max_depth:return self.majority_vote(y,sample_weights)                 #if the depth == max depth
        if feature_names==[]:return self.majority_vote(y,sample_weights)                     #if we have used all the features
        if np.unique(y).shape[0]==1:return self.majority_vote(y,sample_weights)              #if sample of the leaf is pure
        if X.shape[0]<self.min_samples_leaf:return self.majority_vote(y,sample_weights)      #if min sample leaf
        
        best_feature_index=self._choose_best_feature(X,y,sample_weights)                     #get best feature
        best_feature_name=feature_names[best_feature_index]   
        next_best_feature_name=feature_names.copy()                               
        next_best_feature_name.remove(best_feature_name)                                     #remove the beat feature
        values=np.unique(X[:,best_feature_index])                                            #the value of best feature
        subtree=dict()                                                                       #build subtree
        for i in values:
            sub_X, sub_y, sub_sample_weights=self._split_dataset(X,y,best_feature_index,i,sample_weights)# for every value of the best feature
            subtree[i]=self._build_tree(sub_X,sub_y,next_best_feature_name,depth+1,sub_sample_weights)
        mytree[best_feature_name]=subtree
        # end answer
        return mytree

    def predict(self, X):
        """Predict classification results for X.

        Args:
            X: (pd.Dataframe) testing sample features, of shape (N, D).

        Returns:
            (np.array): predicted testing sample labels, of shape (N,).
        """
        if self._tree is None:
            raise RuntimeError("Estimator not fitted, call `fit` first")

        def _classify(tree, x):
            """Classify a single sample with the fitted decision tree.

            Args:
                x: ((pd.Dataframe) a single sample features, of shape (D,).

            Returns:
                (int): predicted testing sample label.
            """
            # YOUR CODE HERE
            # begin answer
            name=list(tree.keys())
            fa_node=name[0]        # get name
            value=x[fa_node]       # get the value of feature
            chil_tree=tree[fa_node]#get the middle tree
            if value not in chil_tree.keys():# if value is not in the feature，just pick one
                value=np.random.choice(list(chil_tree.keys()))
            subtree=chil_tree[value]#get the subtree
            if type(subtree) is not dict:
                return subtree #if not dict then must be a number
            return _classify(subtree,x)

            # end answer

        # YOUR CODE HERE
        # begin answer
        y=np.zeros(X.shape[0])
        for i in range(X.shape[0]):
            _X=X.iloc[i,:]
            y[i]=_classify(self._tree,_X)
        return y
        # end answer

    def show(self):
        """Plot the tree using matplotlib
        """
        if self._tree is None:
            raise RuntimeError("Estimator not fitted, call `fit` first")

        import tree_plotter
        tree_plotter.createPlot(self._tree)
