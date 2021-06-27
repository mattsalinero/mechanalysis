from traitlets.config import Config
import nbformat as nbf
from nbconvert.exporters import HTMLExporter
from nbconvert.preprocessors import TagRemovePreprocessor
from pathlib import Path

def nb_export(notebook, out_path):

    # setup config w/ tags to remove extra code in output report
    c = Config()

    c.TagRemovePreprocessor.remove_cell_tags = ("hide_cell",)
    c.TagRemovePreprocessor.remove_all_outputs_tags = ('hide_output',)
    c.TagRemovePreprocessor.remove_input_tags = ('hide_input',)
    c.TagRemovePreprocessor.enabled = True

    # configure and run exporter
    c.HTMLExporter.preprocessors = ["nbconvert.preprocessors.TagRemovePreprocessor"]

    exporter = HTMLExporter(config=c)
    exporter.register_preprocessor(TagRemovePreprocessor(config=c),True)

    output = HTMLExporter(config=c).from_file(notebook)

    # write to output html file
    with open(out_path,  "w") as out_file:
        out_file.write(output[0])
    
    return
