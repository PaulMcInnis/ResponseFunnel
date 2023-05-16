"""Compare two folders of .JSON containing POSTman responses"""
import os
import json
import argparse
import inspect
import shutil
from jycm.jycm import YouchamaJsonDiffer
from jycm.helper import render_to_html, make_ignore_order_func


def dump_html_output(
    left, right, diff_result, output, left_title="Left", right_title="Right"
):
    # fixed version of the botched one in jcym library where it hardcodes the paths to include my abspath.
    main_script_path = "./index.js"
    html = render_to_html(
        left,
        right,
        diff_result,
        main_script_path=main_script_path,
        left_title=left_title,
        right_title=right_title,
    )
    shutil.copytree(
        os.path.join(
            os.path.dirname(os.path.realpath(inspect.getfile(render_to_html))),
            "jycm_viewer_assets/",
        ),
        output,
    )
    index_url = os.path.join(output, "index.html")
    with open(index_url, "w") as fp:
        fp.write(html)
    return index_url


if __name__ == "__main__":
    # Init a connection to both databases we are comparing
    parser = argparse.ArgumentParser(
        description="compare two folders of reponse .JSON to identify sync issues."
    )
    parser.add_argument(
        "folder_a",
        type=str,
        help="Folder of per-endpoint reponse JSON to compare against.",
    )
    parser.add_argument(
        "folder_b",
        type=str,
        help="Folder of per-endpoint reponse JSON to compare with.",
    )
    parser.add_argument(
        "output",
        type=str,
        help="Folder to store per-endpoint diffs (HTML)",
    )
    args = parser.parse_args()

    # Handle if the output dir exists
    output_dir = os.path.abspath(args.output)
    if os.path.exists(output_dir):
        print(f"output dir '{output_dir}' exists, aborting...")
        exit(1)
    else:
        os.mkdir(output_dir)
    output_raw_diffs = os.path.join(output_dir, "raw.txt")

    # Get the list of files we will compre
    files_a = os.listdir(args.folder_a)
    files_b = os.listdir(args.folder_b)
    common_files = list(set(files_a) & set(files_b))
    common_files.sort()
    header_txt = f"comparing {len(common_files)} common files between {args.folder_a} and {args.folder_b}:"
    print(header_txt)
    if len(common_files) != len(files_a) or len(common_files) != len(files_b):
        raise ValueError("Comparison would exclude requests files from either folder!")

    # Compare one at a time and log the differences
    with open(output_raw_diffs, "w") as raw_log_f:
        raw_log_f.write(header_txt)
        for json_file in common_files:
            if not json_file.endswith(".json"):
                print(f"skipping non-JSON file {json_file}")
                break

            # Load both JSON
            json_a = json.load(open(os.path.join(args.folder_a, json_file)))
            json_b = json.load(open(os.path.join(args.folder_b, json_file)))

            # Calc diff
            ycm = YouchamaJsonDiffer(
                json_a,
                json_b,
                ignore_order_func=make_ignore_order_func(["^ignore_order$"]),
            )
            diff_result = ycm.get_diff()

            # Log the diff and generate interactive HTML viewer for it if there was a difference + write out.
            # NOTE: we avoid dumping diff on empty result {'just4vis:pairs': []} which is always present.
            is_actually_diff = (
                len(diff_result.keys()) > 1
                or len(diff_result.get("just4vis:pairs")) > 1
            )
            diff_txt = "no difference!"
            if is_actually_diff:
                diff_txt = json.dumps(diff_result, sort_keys=True, indent=4)
                dump_diff_folder = os.path.join(output_dir, json_file)
                if diff_result:
                    url = dump_html_output(
                        json_a, json_b, diff_result, dump_diff_folder
                    )
                raw_log_f.write(f"\n\n\tfile: '{json_file}'\n\traw_diff: {diff_txt}")
            # simple console out
            print(f"\t{is_actually_diff}\t\t'{json_file}'")
