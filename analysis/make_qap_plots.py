import argparse
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import pickle
import re
import seaborn as sns
import os

from IPython import embed


def get_hparams():
    parser = argparse.ArgumentParser() 
    parser.add_argument("--summary_df_fname", type=str, required=True, help="summary dataframe filename")
    hparams = parser.parse_args()
    return hparams


if __name__ == "__main__":
    plt.rcParams.update({'font.size': 16})
    plt.gcf().subplots_adjust(left=0.15, bottom=0.15)
    hparams = get_hparams()

    with open(hparams.summary_df_fname, "rb") as f:
        df = pickle.load(f)

    df["warm-start"] = (df["warm_start_strategy"] != "none")

    warm_start_strategy = "none"

    all_data_paths = df["data_path"].unique()
    for data_path in all_data_paths:
        for k_curr in [k for k in df["k_curr"].unique() if k is not None]:
            for k_past in [k for k in df["k_past"].unique() if k is not None]:
                dataset_basename = os.path.basename(data_path).split(".")[0]

                cgal_mask = (df["solver"] == "CGAL")
                k_curr_mask = (df["k_curr"] == k_curr)
                k_past_mask = (df["k_past"] == k_past)
                data_path_mask = (df["data_path"] == data_path)

                subset_mask = cgal_mask | (k_curr_mask & k_past_mask)
                subset_mask &= data_path_mask
                subset_df = df[subset_mask]

                ax = sns.lineplot(
                    subset_df,
                    x="time (sec)",
                    y="relative gap",
                    hue="solver",
                    hue_order=["CGAL", "SpecBM"],
                    style="warm-start",
                    linewidth=2)

                ax.xaxis.set_major_locator(MaxNLocator(integer=True))
                plt.xscale("log")
                plt.grid()
                imgname = "time-vs-gap-{}-{}-{}-{}.png".format(
                    dataset_basename, k_curr, k_past, warm_start_strategy)
                print(f"Saving plot to {imgname}...")
                plt.savefig(imgname)
                plt.clf()
                os.system(f"convert {imgname} -trim {imgname}")

                ax = sns.lineplot(
                    subset_df,
                    x="time (sec)",
                    y="best relative gap",
                    hue="solver",
                    hue_order=["CGAL", "SpecBM"],
                    style="warm-start",
                    linewidth=2)

                ax.xaxis.set_major_locator(MaxNLocator(integer=True))
                plt.xscale("log")
                plt.grid()
                imgname = "time-vs-best_gap-{}-{}-{}-{}.png".format(
                    dataset_basename, k_curr, k_past, warm_start_strategy)
                print(f"Saving plot to {imgname}...")
                plt.savefig(imgname)
                plt.clf()
                os.system(f"convert {imgname} -trim {imgname}")