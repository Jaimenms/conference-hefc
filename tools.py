import json
import os



def save_reports(args, simulation):

    xmlfile1 = '{0}.model.xml'.format(args['input'], )
    simulation.m.SaveModelReport(xmlfile1)
    xmlfile2 = '{0}.model-rt.xml'.format(args['input'], )
    simulation.m.SaveModelReport(xmlfile2)

def inject_external(xmlfile, xmlfile_modified):

    origin_str = ('dae-tools.xsl', 'dae-tools.css')
    destination_str = ('https://s3-us-west-2.amazonaws.com/jaimenms/daetools/dae-tools.xsl',
                       'https://s3-us-west-2.amazonaws.com/jaimenms/daetools/dae-tools.css')

    try:
        with open(xmlfile) as f, open(xmlfile_modified, "w") as g:

            text = f.read()
            for str, str_modified in zip(origin_str, destination_str):
                text = text.replace(str, str_modified)
            g.write(text)
    except:
        print("File not generated")

def convert_to_xhtml(infile, outfile, xslfile):

    from lxml import etree
    xslt_doc = etree.parse(xslfile)
    xslt_transformer = etree.XSLT(xslt_doc)
    source_doc = etree.parse(infile)
    output_doc = xslt_transformer(source_doc)
    output_doc.write(outfile, pretty_print=True)

def get_name(args, data):

    if not args['name']:
        simName = data['name']
    else:
        simName = args['name']

    return simName

def get_names(args):

    # Collect input data
    input_dirname = os.path.dirname(args['input'])
    input_basename = os.path.basename(args['input'])
    input_filename = os.path.splitext(input_basename)[0]

    # Prepare pickle
    pickle_basename = '{0}.simulation'.format(input_filename)
    pickle_file = os.path.join(input_dirname, pickle_basename)

    # Prepare output
    if not args['output']:
        output_basename = '{0}.output.{1}'.format(input_filename, args['format'])
        output_file = os.path.join(input_dirname, output_basename)
        args['output'] = output_file
    else:
        output_file = args['output']

    return (output_file, pickle_file)