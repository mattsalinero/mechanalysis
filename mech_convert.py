from traitlets.config import Config
import nbformat as nbf
from nbconvert.exporters import HTMLExporter
from nbconvert.preprocessors import TagRemovePreprocessor
from pathlib import Path

def main():
    full_nb = Path(__file__).parent / "mech_report.ipynb"
    html_nb = Path(__file__).parent / "mech_report.html"

    if input("generate html report from current jupyter notebook? (CONVERT/N): ").upper() == "CONVERT":
        nb_export(full_nb, html_nb)

    return


def nb_export(notebook, out_path):

    # setup config w/ tags to remove extra code in output report
    c = Config()

    c.TagRemovePreprocessor.remove_cell_tags = ("hide_cell",)
    c.TagRemovePreprocessor.remove_all_outputs_tags = ('hide_output',)
    c.TagRemovePreprocessor.remove_input_tags = ('hide_inputs',)
    c.TagRemovePreprocessor.enabled = True

    # configure and run exporter
    c.HTMLExporter.preprocessors = ["nbconvert.preprocessors.TagRemovePreprocessor"]

    exporter = HTMLExporter(config=c)
    exporter.register_preprocessor(TagRemovePreprocessor(config=c),True)

    output = HTMLExporter(config=c).from_file(notebook)

    # write to output html file
    with open(out_path,  "w", encoding="utf-8") as out_file:
        out_file.write(output[0])
    
    return


if __name__ == '__main__':
    main()