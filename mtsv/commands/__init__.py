import os
import json
import subprocess as sp
import argparse
from mtsv.parsing import create_config_file, file_type, outfile_type
from mtsv.utils import snake_path, get_database_params, error, warn

SNAKEFILES = {
    cmd:snake_path("{}_snek").format(cmd)
    for cmd in [
        "binning", "readprep", "summary",
        "analyze", "analyze_bypass", "analyze_setup",
        "pipeline", "extract",
        "wgfast", "concoct"]}

class Command:
    config_section = []

    def __init__(self, params):
        self._params = params
        self._rules = []

    def __repr__(self):
        return str(self.__class__.__name__)

    @classmethod
    def get_config_line(cls):
        return cls.config_section

    @property
    def params(self):
        return self._params.params
    
    @property
    def snake_params(self):
        return self._params.snake_params
    
    @snake_params.setter
    def snake_params(self, params):
        self._params.snake_params = params

    @property
    def rules(self):
        return self._rules

    @rules.setter
    def rules(self, rules):
        self._rules = rules

    def run(self):
        for rule in self.rules:
            cmd = ["snakemake", "--snakefile", rule, "--config"]
            config = [
                "{0}={1}".format(k,v)
                for k, v in self.params.items() if v is not None]
            cmd += config
            if "--restart-times" not in self.snake_params:
                cmd += ["--restart-times", "3"]
            cmd += self.snake_params
            try:
                p = sp.run(cmd,
                        check=True)
                self._params.write_parameters()
            except ( KeyboardInterrupt, sp.CalledProcessError) as e:
                warn("Unlocking directory after failed snakemake")
                sp.run(cmd + ["--unlock"], check=True )
                error(e)
            

class Init(Command):

    def __init__(self, params):
        super().__init__(params)

    def run(self):
        create_config_file(
            self.params['config'])


class Analyze(Command):
    config_section = ["ANALYZE"]

    def __init__(self, params):
        super().__init__(params)
        self.modify_params()
        self.rules = [SNAKEFILES['analyze_setup']]
    
    def run(self):
        super().run()
        if os.stat(self.params['candidate_taxa_req']).st_size == 0:
            self.rules = [SNAKEFILES['analyze_bypass']]
            super().run()
        else:
            self.rules = [SNAKEFILES['analyze']]
            super().run()
    
    def modify_params(self):
        # trace back params from input files
        self.params['analyze_outpath'] = os.path.dirname(
            self.params['analysis_file'])
        try:
            summary_params = json.loads(open(os.path.join(
                os.path.dirname(self.params['summary_file']),
                ".params"), 'r').read())['summary_file'][self.params['summary_file']]
            merge_file = summary_params['merge_file']
            bin_params = json.loads(open(os.path.join(
                os.path.dirname(merge_file),
                ".params"), 'r').read())['merge_file'][merge_file]
            kmer = json.loads(open(os.path.join(
                os.path.dirname(bin_params['fasta']),
                ".params"), 'r').read())['readprep'][bin_params['fasta']]['kmer']
        except (IOError, ValueError, KeyError) as e:
            error("Problem with input file metadata. "
                  "Avoid moving input files from their original directory "
                  "because the directory contains required metadata" + e)
        self.params['kmer'] = kmer
        for key in ['seed-size', 'min-seeds',
                    'seed-gap', 'edits', 'fm_index_paths',
                    'binning_mode']:
            self.params[key.replace("-", "_")] = bin_params[key]
        self.params['database_config'] = file_type(
            bin_params['database_config'])
        self.params['header'] = []
        self.params['candidate_taxa'] = outfile_type(
                    os.path.join(
                    self.params['analyze_outpath'],
                    "candidate_taxa.txt"))
        self.params['candidate_taxa_req'] = outfile_type(
                    os.path.join(
                    self.params['analyze_outpath'],
                    "candidate_taxa_required.txt"))
        self.params['summary_file_in'] = self.params['summary_file']
        self.params['tax_level'] = summary_params['tax_level']
        # self.params['lca'] = summary_params['lca']
        # move all normal output into analysis subdirectory
        self.params['binning_outpath'] = self.modify_helper("Binning")
        self.params['fasta'] = self.modify_helper("analysis_queries.fasta")
        self.params['merge_file'] = self.modify_helper("Binning/merged.clp")
        self.params['signature_file'] = self.modify_helper("signature.txt")
        self.params['summary_file'] = self.modify_helper("summary.csv")
        try:
            self.params['fasta_db'] = file_type(get_database_params(
                    self.params['database_config'], "fasta-path"
                ))
            self.params['serial_path'] = file_type(get_database_params(
                    self.params['database_config'], "serialization-path"
                ))
        except argparse.ArgumentTypeError:
            error(
                """Database paths used to produce summary file 
                have been moved or deleted""")
            
    def modify_helper(self, filename):
        return os.path.join(
            self.params['analyze_outpath'],
            filename)       
        

class Binning(Command):
    config_section = ["BINNING"]

    def __init__(self, params):
        super().__init__(params)
        self.rules = [SNAKEFILES['binning']]

class Extract(Command):
    config_section=["EXTRACT"]

    def __init__(self, params):
        super().__init__(params)
        self.rules = [SNAKEFILES['extract']]

class Readprep(Command):
    config_section=["READPREP"]

    def __init__(self, params):
        super().__init__(params)
        self.rules = [SNAKEFILES['readprep']]

class Summary(Command):
    config_section=["SUMMARY"]

    def __init__(self, params):
        super().__init__(params)
        self.rules = [SNAKEFILES['summary']]


class Pipeline(Command):
    config_section=["READPREP", "BINNING",
        "SUMMARY", "PIPELINE"]

    def __init__(self, params):
        super().__init__(params)
        self.rules = [SNAKEFILES['pipeline']]

class WGFast(Command):
    config_section=["WGFAST"]
    def __init__(self, params):
        super().__init__(params)
        self.rules = [SNAKEFILES['wgfast']]

class Concoct(Command):
    config_section=["CONCOCT"]
    def __init__(self, params):
        super().__init__(params)
        # add cwd to snakemake command
        self.snake_params = ["--directory", self.params['concoct_output']]
        self.rules = [SNAKEFILES['concoct']]



