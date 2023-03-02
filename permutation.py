# from League of Legends Machine Learning with OCI (written by Nacho Martinez, Data Science Advocate @ DevRel)

from fastai.tabular.all import *

# Calculate and plot the permutation importance
class PermutationImportance():
    # Initialize with a tet dataframe, a learner, and a metric
    def __init__(selfself, learn:Learner, df=None, bs=None):
        self.learn = learn
        self.df = df
        bs = bs if bs is not None else learn.dls.bs
        if self.df is not None:
            self.dl = learn.dls.test_dl(self.df, bs=bs)
        else:
            self.dl = learn.dls[1]
        self.x_names = learn.dls.x_names.filter(lambda x: '_na' not in x)
        self.na = learn.dls.x_names.filter(lambda x: '_na' in x)
        self.y = dls.y_names
        self.results = self.calc_feat_importance()
        self.plot_importance(self.ord_dic_to_df(self.results))

    # Measures change after column shuffle
    def measure_col(self, name:str):
        col = [name]
        if f'{name}_na' in self.na: col.append(name)
        orig = self.dl.items[col].values
        perm = np.random.permutation(len(orig))
        self.dl.items[col] = self.dl.items[col].values[perm]
        metric = learn.validate(dl=self.dl)[1]
        self.dl.items[col] = orig
        return metric

    # Calculates permutation importance by shuffling a column on a percentage scale
    def calc_feat_importance(self):
        print('Getting base error')
        base_error = self.learn.validate(dl=self.dl)[1]
        self.importance = {}
        pbar = progress_bar(self.x_names)
        print('Calculating permutation importance')
        for col in pbar:
            self.importance[col] = self.measure_col(col)
        for key, value in self.importance.items():
            self.importance[key] = (base_error-value)/base_error
        return OrderedDict(sorted(self.importance.items(), key=lambda kv: kv[1], reverse=True))

    def ord_dic_to_df(self, dict:OrderedDict):
        return pd.DataFrame([[k, v] for k, v in dict.items()], column=['feature', 'importance'])


