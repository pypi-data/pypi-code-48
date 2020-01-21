from datetime import date

from janis_core import File, String, Array, InputSelector, WorkflowMetadata, ScatterDescription, ScatterMethods

from janis_bioinformatics.data_types import (
    FastaWithDict,
    VcfTabix,
    FastqGzPair,
    Bed,
    Bam,
    BamBai,
)
from janis_bioinformatics.tools.babrahambioinformatics import FastQC_0_11_5
from janis_bioinformatics.tools.bcftools import BcfToolsSort_1_9
from janis_bioinformatics.tools.bioinformaticstoolbase import BioinformaticsWorkflow
from janis_bioinformatics.tools.common import BwaAligner, MergeAndMarkBams_4_1_3
from janis_bioinformatics.tools.gatk4 import Gatk4GatherVcfs_4_0, Gatk4SortSam_4_1_3
from janis_bioinformatics.tools.variantcallers import GatkGermlineVariantCaller_4_1_3
from janis_bioinformatics.tools.pmac import ParseFastqcAdaptors


class WGSGermlineGATK(BioinformaticsWorkflow):
    def id(self):
        return "WGSGermlineGATK"

    def friendly_name(self):
        return "WGS Germline (GATK only)"

    @staticmethod
    def version():
        return "1.2.0"

    def constructor(self):

        self.input("fastqs", Array(FastqGzPair))
        self.input("reference", FastaWithDict)
        self.input("cutadapt_adapters", File)
        self.input("gatk_intervals", Array(Bed))

        self.input("sample_name", String(), default="NA12878")

        self.input("snps_dbsnp", VcfTabix, doc="")
        self.input("snps_1000gp", VcfTabix)
        self.input("known_indels", VcfTabix)
        self.input("mills_indels", VcfTabix)

        # STEPS

        self.step("fastqc", FastQC_0_11_5(reads=self.fastqs), scatter="reads")
        
        self.step(
            "getfastqc_adapters", 
            ParseFastqcAdaptors(
                fastqc_datafiles=self.fastqc.datafile,
                cutadapt_adaptors_lookup=self.cutadapt_adapters
            ),
            scatter="fastqc_datafiles"
        )

        self.step(
            "align_and_sort",
            BwaAligner(
                fastq=self.fastqs,
                reference=self.reference,
                sample_name=self.sample_name,
                sortsam_tmpDir=".",
                cutadapt_adapter=self.getfastqc_adapters,
                cutadapt_removeMiddle3Adapter=self.getfastqc_adapters
            ),
            scatter=["fastq", "cutadapt_adapter", "cutadapt_removeMiddle3Adapter"]
        )

        self.step("merge_and_mark", MergeAndMarkBams_4_1_3(bams=self.align_and_sort))

        # VARIANT CALLERS

        # GATK
        self.step(
            "vc_gatk",
            GatkGermlineVariantCaller_4_1_3(
                bam=self.merge_and_mark,
                intervals=self.gatk_intervals,
                reference=self.reference,
                snps_dbsnp=self.snps_dbsnp,
                snps_1000gp=self.snps_1000gp,
                known_indels=self.known_indels,
                mills_indels=self.mills_indels,
            ),
            scatter="intervals",
        )

        self.step(
            "vc_gatk_merge",
            Gatk4GatherVcfs_4_0(vcfs=self.vc_gatk.out),
        )
        # sort

        self.step(
            "sort_combined", BcfToolsSort_1_9(vcf=self.vc_gatk_merge.out)
        )


        self.output(
            "bam", source=self.merge_and_mark.out, output_folder=["bams", self.sample_name]
        )
        self.output(
            "reports", source=self.fastqc.out, output_folder=["reports", self.sample_name]
        )
        self.output("variants", source=self.sort_combined.out, output_folder="variants")
        self.output(
            "variants_split",
            source=self.vc_gatk.out,
            output_folder=["variants", "byInterval"],
        )

    def bind_metadata(self):
        meta: WorkflowMetadata = self.metadata

        meta.keywords = ["wgs", "cancer", "germline", "variants", "gatk"]
        meta.contributors = ["Michael Franklin"]
        meta.dateUpdated = date(2019, 10, 16)
        meta.short_documentation = "A variant-calling WGS pipeline using only the GATK Haplotype variant caller."


if __name__ == "__main__":
    import os.path
    w = WGSGermlineGATK()
    args = {
        "to_console": False,
        "to_disk": True,
        "validate": True,
        "export_path": os.path.join(os.path.dirname(os.path.realpath(__file__)), "{language}"),
    }
    w.translate("cwl", **args)
    w.translate("wdl", **args)
