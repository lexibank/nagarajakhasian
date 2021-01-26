from pathlib import Path

from clldutils.misc import slug

import pylexibank


class Dataset(pylexibank.Dataset):
    dir = Path(__file__).parent
    id = "nagarajakhasian"

    # define the way in which forms should be handled
    form_spec = pylexibank.FormSpec(
        brackets={"(": ")"},  # characters that function as brackets
        separators=";/,",  # characters that split forms e.g. "a, b".
        missing_data=('(?)', '-', '--'),  # characters that denote missing data.
        strip_inside_brackets=True   # do you want data removed in brackets or not?
    )

    def cmd_download(self, args):
        pass
        
    def cmd_makecldf(self, args):
        """
        Convert the raw data to a CLDF dataset.
        """

        languages = args.writer.add_languages(
            lookup_factory=lambda l: l['Name']
        )
        
        concepts = args.writer.add_concepts(
            id_factory=lambda c: c.id.split('-')[-1]+ '_' + slug(c.english),
            lookup_factory="Name"
        )
        
        # handle some mismatches.
        concepts.update({
            'to blow': '16_blow',
            'to breathe': '18_breathe',
            'to burn': '19_burn',
            'to come': '23_come',
            'to count': '24_count',
            'to cut': '25_cut',
            'to die': '27_die',
            'to dig': '28_dig',
            'to dry': '32_dry',
            'to give': '60_give',
            'to hear': '69_hear',
            'to hit': '73_hit',
            'to hold-take': '74_holdtake',
            'to hunt': '76_hunt',
            'to kill': '82_kill',
            'to know': '83_know',
            'to laugh': '85_laugh',
            'left side': '87_leftside',
            'to live': '90_live',
            'to see': '130_see',
            'sharp (blade)': '133_sharp',
        })
        
        args.writer.add_sources()

        header = ['Khasi', 'Lyngngam', 'Pnar/Jaintia', 'War/Lamin', 'Palaung', 'Khmu']
        
        for row in self.raw_dir.read_csv('khasian4x200-plus#170413.tsv', dicts=True, delimiter="\t"):
            param_id = concepts.get(row['Gloss'].strip())
            for idx, lang in enumerate(header):
                
                # figure out cognate sets and loanwords
                is_loan = False
                # asterisks indicate not cognate loan words
                if row['Scores'][idx] == '*':
                    cog = None
                    is_loan = True
                # otherwise should be in a-f
                elif row['Scores'][idx].lower() in 'abcdef':
                    cog = "%s_%s" % (param_id, row['Scores'][idx].lower())
                else:
                    raise ValueError("Bad Cognate set: %s" % row['Scores'][idx])
                
                lex = args.writer.add_forms_from_value(
                    Language_ID=lang.replace("/", ""),
                    Parameter_ID=param_id,
                    Value=row[lang],
                    Source=['Nagaraja2013'],
                    Cognacy=cog,
                    Loan=is_loan
                )

                if cog and len(lex):
                    args.writer.add_cognate(lexeme=lex[0], Cognateset_ID=cog)
