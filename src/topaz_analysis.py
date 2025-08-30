#!/usr/bin/env python3
"""
Topaz analysis subroutines for cryoDL.

This module contains analysis functions for Topaz results, including
cross-validation analysis and performance evaluation.
"""

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from PIL import Image
import glob
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging

# Try to import topaz utilities, but don't fail if not available
try:
    from topaz.utils.data.loader import load_image

    TOPAZ_AVAILABLE = True
except ImportError:
    TOPAZ_AVAILABLE = False
    logging.warning("Topaz utilities not available. Some functions may not work.")


def analyze_cross_validation(
    cv_dir: str,
    n_values: List[int] = [250, 300, 350, 400, 450, 500],
    k_folds: int = 5,
    output_dir: Optional[str] = None,
    save_plots: bool = True,
    show_plots: bool = False,
) -> Dict:
    """
    Analyze cross-validation results from Topaz training.

    This function loads cross-validation results, calculates performance metrics,
    generates plots, and provides recommendations for optimal hyperparameters.

    Args:
        cv_dir: Directory containing cross-validation results
        n_values: List of N values used in cross-validation
        k_folds: Number of folds used in cross-validation
        output_dir: Directory to save analysis results (defaults to cv_dir)
        save_plots: Whether to save generated plots
        show_plots: Whether to display plots interactively

    Returns:
        Dictionary containing analysis results including:
        - cv_results: Full cross-validation results DataFrame
        - cv_results_mean: Mean results across folds
        - cv_results_epoch: Best epoch results for each N
        - best_n: Recommended N value
        - best_epoch: Recommended number of epochs
        - plots: Dictionary of generated plots
    """

    cv_path = Path(cv_dir)
    if not cv_path.exists():
        raise FileNotFoundError(f"Cross-validation directory not found: {cv_dir}")

    if output_dir is None:
        output_dir = cv_dir
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"Analyzing cross-validation results from: {cv_dir}")
    print(f"Output directory: {output_dir}")

    # Load cross-validation results
    tables = []
    for n in n_values:
        for fold in range(k_folds):
            path = cv_path / f"model_n{n}_fold{fold}_training.txt"
            if path.exists():
                try:
                    table = pd.read_csv(path, sep="\t")
                    table["N"] = n
                    table["fold"] = fold
                    # Only keep the validation results
                    table = table.loc[table["split"] == "test"]
                    tables.append(table)
                    print(f"Loaded results for N={n}, fold={fold}")
                except Exception as e:
                    print(f"Warning: Could not load {path}: {e}")
            else:
                print(f"Warning: File not found: {path}")

    if not tables:
        raise ValueError("No cross-validation results found!")

    # Combine all results
    cv_results = pd.concat(tables, axis=0, ignore_index=True)
    cv_results["auprc"] = cv_results["auprc"].astype(float)

    print(f"Loaded {len(cv_results)} validation results")
    print(f"Results shape: {cv_results.shape}")

    # Calculate mean AUPRC for each condition and each epoch
    cv_results_mean = (
        cv_results.groupby(["N", "epoch"]).mean().reset_index().drop("fold", axis=1)
    )

    # Find best epoch results for each N
    cv_results_epoch = (
        cv_results_mean.groupby("N")
        .apply(lambda x: x.loc[x["auprc"].idxmax()])
        .reset_index(drop=True)
    )

    # Find overall best parameters
    best_row = cv_results_epoch.loc[cv_results_epoch["auprc"].idxmax()]
    best_n = int(best_row["N"])
    best_epoch = int(best_row["epoch"])
    best_auprc = best_row["auprc"]

    print(f"\nCross-validation Analysis Results:")
    print(f"Best N value: {best_n}")
    print(f"Best number of epochs: {best_epoch}")
    print(f"Best AUPRC: {best_auprc:.4f}")

    # Generate plots
    plots = {}

    # Plot 1: AUPRC vs Epoch for each N
    plt.figure(figsize=(12, 8))
    for n in n_values:
        result = cv_results_mean[cv_results_mean["N"] == n]
        if not result.empty:
            plt.plot(
                result["epoch"],
                result["auprc"],
                "-o",
                label=f"N={n}",
                linewidth=2,
                markersize=6,
            )

    plt.xlabel("Epoch", fontsize=12)
    plt.ylabel("AUPRC", fontsize=12)
    plt.title("Cross-validation Performance: AUPRC vs Epoch", fontsize=14)
    plt.legend(loc="best", fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    if save_plots:
        plot_path = output_path / "cv_performance_vs_epoch.png"
        plt.savefig(plot_path, dpi=300, bbox_inches="tight")
        print(f"Saved performance plot: {plot_path}")

    plots["performance_vs_epoch"] = plt.gcf()

    if show_plots:
        plt.show()
    else:
        plt.close()

    # Plot 2: Best AUPRC for each N
    plt.figure(figsize=(10, 6))
    plt.plot(
        cv_results_epoch["N"],
        cv_results_epoch["auprc"],
        "-o",
        linewidth=2,
        markersize=8,
    )
    plt.axvline(
        x=best_n, color="red", linestyle="--", alpha=0.7, label=f"Best N={best_n}"
    )
    plt.xlabel("N (Expected particles per micrograph)", fontsize=12)
    plt.ylabel("Best AUPRC", fontsize=12)
    plt.title("Best Cross-validation Performance by N Value", fontsize=14)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    if save_plots:
        plot_path = output_path / "cv_best_performance_by_n.png"
        plt.savefig(plot_path, dpi=300, bbox_inches="tight")
        print(f"Saved best performance plot: {plot_path}")

    plots["best_performance_by_n"] = plt.gcf()

    if show_plots:
        plt.show()
    else:
        plt.close()

    # Plot 3: Heatmap of AUPRC vs N and Epoch
    plt.figure(figsize=(12, 8))

    # Create pivot table for heatmap
    heatmap_data = cv_results_mean.pivot(index="epoch", columns="N", values="auprc")

    # Create heatmap
    im = plt.imshow(heatmap_data.T, cmap="viridis", aspect="auto", origin="lower")
    plt.colorbar(im, label="AUPRC")

    # Set axis labels
    plt.xlabel("Epoch", fontsize=12)
    plt.ylabel("N Value", fontsize=12)
    plt.title("AUPRC Heatmap: N vs Epoch", fontsize=14)

    # Set tick labels
    plt.xticks(range(len(heatmap_data.index)), heatmap_data.index)
    plt.yticks(range(len(heatmap_data.columns)), heatmap_data.columns)

    plt.tight_layout()

    if save_plots:
        plot_path = output_path / "cv_auprc_heatmap.png"
        plt.savefig(plot_path, dpi=300, bbox_inches="tight")
        print(f"Saved heatmap: {plot_path}")

    plots["auprc_heatmap"] = plt.gcf()

    if show_plots:
        plt.show()
    else:
        plt.close()

    # Save results to CSV
    results_summary_path = output_path / "cv_analysis_summary.csv"
    cv_results_epoch.to_csv(results_summary_path, index=False)
    print(f"Saved analysis summary: {results_summary_path}")

    # Create detailed results file
    detailed_results_path = output_path / "cv_detailed_results.csv"
    cv_results_mean.to_csv(detailed_results_path, index=False)
    print(f"Saved detailed results: {detailed_results_path}")

    # Generate recommendations
    recommendations = {
        "best_n": best_n,
        "best_epoch": best_epoch,
        "best_auprc": best_auprc,
        "recommendation": f"Train with N={best_n} for at least {best_epoch} epochs. "
        f"Consider training longer as performance may continue to improve.",
        "all_results": cv_results_epoch.to_dict("records"),
    }

    # Save recommendations to text file
    recommendations_path = output_path / "cv_recommendations.txt"
    with open(recommendations_path, "w") as f:
        f.write("Cross-validation Analysis Recommendations\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Best N value: {best_n}\n")
        f.write(f"Best number of epochs: {best_epoch}\n")
        f.write(f"Best AUPRC: {best_auprc:.4f}\n\n")
        f.write("Recommendation:\n")
        f.write(recommendations["recommendation"] + "\n\n")
        f.write("Detailed Results:\n")
        f.write(cv_results_epoch.to_string())

    print(f"Saved recommendations: {recommendations_path}")

    return {
        "cv_results": cv_results,
        "cv_results_mean": cv_results_mean,
        "cv_results_epoch": cv_results_epoch,
        "best_n": best_n,
        "best_epoch": best_epoch,
        "best_auprc": best_auprc,
        "recommendations": recommendations,
        "plots": plots,
        "output_dir": str(output_dir),
    }


def plot_training_curves(
    training_files: List[str],
    output_dir: str,
    save_plots: bool = True,
    show_plots: bool = False,
) -> None:
    """
    Plot training curves from Topaz training files.

    Args:
        training_files: List of paths to training result files
        output_dir: Directory to save plots
        save_plots: Whether to save generated plots
        show_plots: Whether to display plots interactively
    """

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for file_path in training_files:
        try:
            # Load training data
            data = pd.read_csv(file_path, sep="\t")

            # Extract model name from file path
            model_name = Path(file_path).stem

            # Create training curves plot
            plt.figure(figsize=(12, 8))

            # Plot training and validation metrics
            if "train_auprc" in data.columns and "test_auprc" in data.columns:
                plt.subplot(2, 2, 1)
                plt.plot(data["epoch"], data["train_auprc"], label="Train AUPRC")
                plt.plot(data["epoch"], data["test_auprc"], label="Test AUPRC")
                plt.xlabel("Epoch")
                plt.ylabel("AUPRC")
                plt.title(f"{model_name} - AUPRC")
                plt.legend()
                plt.grid(True, alpha=0.3)

            if "train_loss" in data.columns and "test_loss" in data.columns:
                plt.subplot(2, 2, 2)
                plt.plot(data["epoch"], data["train_loss"], label="Train Loss")
                plt.plot(data["epoch"], data["test_loss"], label="Test Loss")
                plt.xlabel("Epoch")
                plt.ylabel("Loss")
                plt.title(f"{model_name} - Loss")
                plt.legend()
                plt.grid(True, alpha=0.3)

            if "train_precision" in data.columns and "test_precision" in data.columns:
                plt.subplot(2, 2, 3)
                plt.plot(
                    data["epoch"], data["train_precision"], label="Train Precision"
                )
                plt.plot(data["epoch"], data["test_precision"], label="Test Precision")
                plt.xlabel("Epoch")
                plt.ylabel("Precision")
                plt.title(f"{model_name} - Precision")
                plt.legend()
                plt.grid(True, alpha=0.3)

            if "train_recall" in data.columns and "test_recall" in data.columns:
                plt.subplot(2, 2, 4)
                plt.plot(data["epoch"], data["train_recall"], label="Train Recall")
                plt.plot(data["epoch"], data["test_recall"], label="Test Recall")
                plt.xlabel("Epoch")
                plt.ylabel("Recall")
                plt.title(f"{model_name} - Recall")
                plt.legend()
                plt.grid(True, alpha=0.3)

            plt.tight_layout()

            if save_plots:
                plot_path = output_path / f"{model_name}_training_curves.png"
                plt.savefig(plot_path, dpi=300, bbox_inches="tight")
                print(f"Saved training curves: {plot_path}")

            if show_plots:
                plt.show()
            else:
                plt.close()

        except Exception as e:
            print(f"Warning: Could not plot training curves for {file_path}: {e}")


def main():
    """Example usage of the analysis functions."""

    # Example: Analyze cross-validation results
    cv_dir = "saved_models/EMPIAR-10025/cv"

    if Path(cv_dir).exists():
        print("Running cross-validation analysis...")
        results = analyze_cross_validation(
            cv_dir=cv_dir,
            n_values=[250, 300, 350, 400, 450, 500],
            k_folds=5,
            output_dir="analysis_results",
            save_plots=True,
            show_plots=False,
        )

        print(f"\nAnalysis complete!")
        print(f"Best N: {results['best_n']}")
        print(f"Best epochs: {results['best_epoch']}")
        print(f"Best AUPRC: {results['best_auprc']:.4f}")
    else:
        print(f"Cross-validation directory not found: {cv_dir}")
        print("Please run cross-validation first using the 'topaz cross' command.")


if __name__ == "__main__":
    main()
