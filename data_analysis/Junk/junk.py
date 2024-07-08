# Use hierarchical indexing with pandas
"""
    1. Create df as normal
    2. df.set_index(['col1', 'col2', 'col3'])
        -simply pass several columns to index
    3. df.loc[("999", "HFG", 1), 'aware']
        -for each subject and trans_dur to get individual judgments
        -remove outliers from these data
        -levels can be passed as arguments to the function
"""


# Create hierarchical index in pandas
d = data.data.set_index(index)
d.sort_index() # This improves performance and allows partial splicing

# def do_box_swarm2():
#     """Look at a separate plot for each factor.
#         Collapsed across durations. 
#     """
#     for sub in subs:
#         for level in levels:
#             #for dur in durs:
#             x = d.loc[(sub, slice(None), slice(None)), level]
#             print(x)
#             data.mk_boxplot(data=x, factor_colname='condition', value_colname=level)

# #do_box_swarm2()


# All ratings by duration
def swarm_all():
    num_plots = len(conds) * len(levels)

    for sub in subs:
        ii_factor = 0
        for cond in conds:
            for level in levels:
                ii_factor += 1
                plt.subplot(num_plots, 1, ii_factor)
                x = d.loc[(sub, cond, slice(None)), level]
                x = pd.DataFrame(x)
                x = x.reset_index()

                ax = sns.boxplot(
                    x='trans_dur', 
                    y=level, 
                    data=x
                    )

                ax = sns.swarmplot(
                    x='trans_dur', 
                    y=level, 
                    data=x
                    )
                plt.title(f"SS {sub} '{level.upper()}' Ratings for '{cond}'")
                plt.xlabel("Transition Duration")
                plt.ylabel(f"{level.upper()} Rating")
                plt.ylim([-1,101])
        plt.show()

#swarm_all()


# All ratings by condition
def swarm_cond(condition):
    num_plots = len(factors)

    for sub in subs:
        ii_factor = 0
        for factor in factors:
            ii_factor += 1
            plt.subplot(num_plots, 1, ii_factor)
            x = d.loc[(sub, condition, slice(None)), factor]
            x = pd.DataFrame(x)
            x = x.reset_index()

            ax = sns.boxplot(
                x='trans_dur', 
                y=factor, 
                data=x
                )

            ax = sns.swarmplot(
                x='trans_dur', 
                y=factor, 
                data=x
                )
            plt.title(f"SS {sub} '{factor.upper()}' Ratings for '{condition}'")
            plt.xlabel("Transition Duration")
            plt.ylabel(f"{factor.capitalize()} Rating")
            plt.ylim([0,100])
        plt.show()

#swarm_cond('HFG')



    # This is now just done in the script itself
    # #def mk_boxplot(self, data, factor_colname, value_colname):
    # def mk_boxplot(self, data, title):
    #     """Display box plot and swarm plot for data by factor.
    #     """
    #     #data = pd.DataFrame(data)
    #     #data = data.reset_index()

    #     ax = sns.boxplot(
    #         x=factor_colname,
    #         y=value_colname,
    #         data=data
    #         )
    #     ax = sns.swarmplot(
    #         x=factor_colname, 
    #         y=value_colname, 
    #         data=data, 
    #         color='k'
    #         )
    #     plt.title(f"'{title.upper()}' data for subject {data['subject'][0]}")
    #     plt.show()




def delete_outliers():
    """Identify and remove outliers.
    """
    clean_data = []
    for sub in subs:
        for cond in conds:
            for level in levels:
                for dur in durs:
                    x = d.loc[(sub, cond, dur), level]
                    num_outliers, clean = data.remove_outliers(vals=x, dist='symmetrical', k=3, plts='n')
                    if num_outliers > 0:
                        print(f"Found {num_outliers} outliers for index {sub}, {cond}, {dur}, {level}")
                    clean_df = pd.DataFrame(clean)
                    #clean_df.reset_index()
                    #clean_df.sort_index()
                    clean_data.append(clean_df)

    # Add newly-cleaned dataframe to object: self.clean_data
    # Retain original dataset as: self.data
    clean_data_df = pd.concat(clean_data)
    data.clean_data = clean_data_df

delete_outliers()



def outliers_plot(condition):
    num_plots = len(factors)

    # Make hierarchical index from cleaned data
    #clean = data.clean_data.set_index(index)
    #clean.sort_index()

    for sub in subs:
        ii_factor = 0
        for factor in factors:
            ii_factor += 1
            plt.subplot(num_plots, 1, ii_factor)
            x = d.loc[(sub, condition, slice(None)), factor]
            y = clean.loc[(sub, condition, slice(None)), factor]

            x = pd.DataFrame(x)
            x = x.reset_index()
            y = pd.DataFrame(y)
            y = x.reset_index()

            ax = sns.swarmplot(
                x='trans_dur', 
                y=factor,
                color='red',
                data=x
                )

            ax = sns.swarmplot(
                x='trans_dur', 
                y=factor, 
                color='green',
                data=y
                )
            plt.title(f"SS {sub} '{factor.upper()}' Ratings for '{condition}'")
            plt.xlabel("Transition Duration")
            plt.ylabel(f"{factor.capitalize()} Rating")
            plt.ylim([0,100])
        plt.show()

#outliers_plot('HFG')



def outliers_plot(condition):
    num_plots = len(factors)
    for sub in subs:
        ii_factor = 0
        for factor in factors:
            ii_factor += 1
            plt.subplot(num_plots, 1, ii_factor)
            x = d.loc[(sub, condition, slice(None)), factor]
            y = clean.loc[(sub, condition, slice(None)), factor]

            x = pd.DataFrame(x)
            x = x.reset_index()
            y = pd.DataFrame(y)
            y = x.reset_index()

            ax = sns.swarmplot(
                x='trans_dur', 
                y=factor,
                color='red',
                data=x
                )

            ax = sns.swarmplot(
                x='trans_dur', 
                y=factor, 
                color='green',
                data=y
                )
            plt.title(f"SS {sub} '{factor.upper()}' Ratings for '{condition}'")
            plt.xlabel("Transition Duration")
            plt.ylabel(f"{factor.capitalize()} Rating")
            plt.ylim([0,100])
        plt.show()

#outliers_plot('HFG')