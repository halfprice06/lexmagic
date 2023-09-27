from textual.app import App, ComposeResult
from textual.widgets import Tree
import pandas as pd

class FinalRevisedHierarchyApp(App):
    
    def __init__(self, data: pd.DataFrame, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = data

    def compose(self) -> ComposeResult:
        tree: Tree[dict] = Tree("Legal Hierarchy")
        tree.root.expand()

        # Helper function to add articles to nodes
        def add_articles_to_node(node, group):
            for _, article_row in group.iterrows():
                article_title = f"{article_row['article_number']} - {article_row['article_title']}"
                node.add_leaf(article_title)

        # Group data by hierarchical levels
        for _, book_group in self.data.groupby('BOOK'):
            book_node = tree.root.add(book_group['BOOK'].iloc[0], expand=True)

            # Add articles directly under book if there are no titles
            if book_group['TITLE'].isna().all():
                add_articles_to_node(book_node, book_group)

            for _, title_group in book_group.groupby('TITLE'):
                title_node = book_node.add(title_group['TITLE'].iloc[0], expand=True) if not pd.isna(title_group['TITLE'].iloc[0]) else book_node

                # Add articles directly under title if there are no chapters
                if title_group['CHAPTER'].isna().all():
                    add_articles_to_node(title_node, title_group)

                for _, chapter_group in title_group.groupby('CHAPTER'):
                    chapter_node = title_node.add(chapter_group['CHAPTER'].iloc[0], expand=True) if not pd.isna(chapter_group['CHAPTER'].iloc[0]) else title_node

                    # Add articles directly under chapter if there are no sections
                    if chapter_group['SECTION'].isna().all():
                        add_articles_to_node(chapter_node, chapter_group)

                    for _, section_group in chapter_group.groupby('SECTION'):
                        section_node = chapter_node.add(section_group['SECTION'].iloc[0], expand=True) if not pd.isna(section_group['SECTION'].iloc[0]) else chapter_node

                        # Add articles directly under section if there are no subsections
                        if section_group['SUBSECTION'].isna().all():
                            add_articles_to_node(section_node, section_group)

                        for _, subsection_group in section_group.groupby('SUBSECTION'):
                            if pd.isna(subsection_group['SUBSECTION'].iloc[0]):
                                add_articles_to_node(section_node, subsection_group)
                            else:
                                subsection_node = section_node.add(subsection_group['SUBSECTION'].iloc[0], expand=True)
                                add_articles_to_node(subsection_node, subsection_group)
        
        yield tree
app = FinalRevisedHierarchyApp(pd.read_csv("articles.csv"))
app.run()
