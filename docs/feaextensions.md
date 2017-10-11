# FEA Extensions

## Introduction

This document is where people can dream of the extensions they would like to see added to FEA. Notice that any extensions need to be convertible back to normal FEA so shouldn't do things that can't be expressed in FEA.

There are a number of possible things that can be added to FEA, the question is whether they are worth adding in terms of meeting actual need (remove from this list if added to the rest of the document):

*   classsubtract() classand() functions
    *   classand(x, y) = classsubtract(x, (classsubtract(x, y))
*   classbuild(class, "$.ext") builds one class out of another. What if something is missing? Or do we just build those classes on the fly from make_fea and glyph name parsing?

## Statements

Statements are used to make rules, lookups, etc.

### setadvance

This function does the calculations necessary to adjust the advance of a glyph based on information of attachment points, etc. The result is a single shift on each of the glyphs in the class. The syntax is:

```
setadvance(@glyphs, APName [, attachedGlyph[, APName, attachedGlyph [...]]])
```

In effect there are two modes for this function. The first only has two parameters and shifts the advance from its default designed position to the x co-ordinate of the given attachment point. The second mode adds extra glyphs. The advance is moved to the advance of the attachedGlyph assuming the base has the other glyphs chained attached at their given APs. An AP may be a number in which case that is the x co-ordinate of the AP that will be used.

Typically there will be only one of these per lookup, unless the classes referenced are non overlapping.

#### Examples

These examples also act as motivating use cases.

##### Nokyung

In Nokyung there is a need to kern characters that do not descend below the baseline closer to glyphs with a right underhang. This can be done through kerning pairs or we could add an attachment point to the glyphs with the right underhang and contextual adjust their advances to that position. The approach of using an AP to do kerning is certainly quirky and few designers would go that route. The contextual lookup would call a lookup that just does the single adjustment. Consider the AP to be called K (for kern). The fea might look like:

```
lookup overhangKernShift {
    setadvance(@overhangs, K);
} overhangKernShift;
```

And would expand, potentially, into

```
lookup overhangKernShift {
    @overhangs <-80>;
} overhangKernShift;
```
Not much, but that is because in Nokyung the overhanging glyphs all have the same overhang. If they didn't, then the list could well expand with different values for each glyph in the overhangs class. In fact, a simple implementation would do such an expansion anyway, while a more sophisticated implementation would group the results into ad hoc glyph lists.

##### Myanmar

An example from Myanmar is where a diacritic is attached such that the diacritic overhangs the right hand side of the base glyph and we want to extend the advance of the base glyph to encompass the diacritic. This is a primary motivating example for this statement. Such a lookup might read:

```
lookup advanceForLDotOnU {
    setadvance(@base, L, uvowel, LD, ldot);
} advanceForLDotOnU;
```

Which transforms to:

```
lookup advanceForLDotOnU {
    ka <120>;
    kha <80>;
# …
} advanceForLDotOnU;
```

#### Issues

*   Do we want to use a syntax more akin to that used for composites, since that is, in effect, what we are describing: make the base have the advance of the composite?
*   Do we want to change the output to reflect the sequence so that there can be more statements per lookup?
    *   The problem is that then you may want to skip intervening non-contributing glyphs (like upper diacritics in the above examples), which you would do anyway from the contextual driving lookup, but wouldn't want to have to do in each situation here.
*   It's a bit of a pain that in effect there is only one setadvance() per lookup. It would be nice to do more.
*   Does this work (and have useful meaning) in RTL?
*   Appears to leave the base glyph *position* unchanged. Is there a need to handle, for example in LTR scripts, LSB change for a base due to its diacritics? (Think i-tilde, etc.)

### baseclass ✓

A baseclass is the base equivalent of a markclass. It specifies the position of a particular class of anchor points on a base, be that a true base or a mark base. The syntax is the same as for a markclass, but it is used differently in a pos rule:

```
markClass [acute] <anchor 350 0> @TOP_MARKS;
baseClass [a] <anchor 500 500> @BASE_TOPS;
baseClass b <anchor 500 750> @BASE_TOPS;

feature test {
		pos base @BASE_TOPS mark @TOP_MARKS;
} test;
```

Which is the functional equivalent of:

```
markClass [acute] <anchor 350 0> @TOP_MARKS;

feature test {
		pos base [a] <anchor 500 500> mark @TOP_MARKS;
		pos base b <anchor 500 750> mark @TOP_MARKS;
} test;
```

It should be borne in mind that both markClasses and baseClasses can also be used as normal glyph classes and as such use the same namespace.

The baseClass statement is a high priority need in order to facilitate auto generation of attachment point information without having to create what might be redundant lookups in the wrong order.

#### Cursive Attachment ✓

Cursive attachment involves two base anchors, one for the entry and one for the exit. We can extend the use of baseClasses to support this, by passing two baseClasses to the pos cursive statement:

```
baseClass meem.medial <anchor 700 50> @ENTRIES;
baseClass meem.medial <anchor 0 10> @EXITS;

feature test {
		pos cursive @ENTRIES @EXITS;
	} test;
```

Here we have two base classes for the two anchor points, and the pos cursive processing code works out which glyphs are in both classes, and which are in one or the other and generates the necessary pos cursive statement for each glyph. I.e. there will be statements for the union of the two classes but with null anchors for those only in one (according to which baseClass they are in). This has the added advantage that any code generating baseClasses does not need to know whether a particular attachment point is being used in a cursive attachment. That is entirely up to the user of the baseClass.

#### Mark Attachment ⍻

The current mark attachment syntax is related to the base mark attachment in that the base mark has to be specified explicitly and we cannot currently use a markclass as the base mark in a mark attachment lookup. We can extend the mark attachment in the same way as we extend the base attachment, by allowing the mark base to be a markclass. Thus:

```
pos mark @MARK_BASE_CLASS mark @MARK_MARK_CLASS;
```

Would expand out to a list of mark mark attachment rules.

### move

The move semantic results in a complex of lookups. See this [article](https://github.com/OpenType/opentype-layout/blob/master/docs/ligatures.md) on how to implement a move semantic successfully in OpenType. As such a move semantic can only be expressed as a statement at the highest level since it creates lookups. The move statement takes a number of parameters:

```
move lookup_basename, skipped, matched;
```

The *lookup_basename* is a name (unadorned string) prefix that is used in the naming of the lookups that the move statement creates. It also allows multiple move statements to share the same lookups where appropriate. Such lookups can be referenced by contextual chaining lookups. The lookups generated are:

|                              |                                                    |
| ---------------------------- | -------------------------------------------------- |
| lookup_basename_match        | Contextual chaining lookup to drive the sublookups |
| lookup_basename_pres_matched | Converts skipped(1) to matched + skipped(1) |
| lookup_basename_pref_matched | Converts skipped(1) to matched + skipped(1) + matched |
| lookup_basename_back         | Converts skipped(-1) + matched to skipped(-1). |

Multiple instances of a move statement that use the same *lookup_basename* will correctly merge the various rules in the the lookups created since often at least parts of the *skipped* or *matched* will be the same across different statements.

Since lookups may be added to, extra contextual rules can be added to the *lookup_basename*_match.

*skipped* contains a sequence of glyphs (of minimum length 1), where each glyph may be a class or whatever. The move statement considers both the first and last glyph of this sequence when it comes to the other lookups it creates. *skipped(1)* is the first glyph in the sequence and *skipped(-1)* is the last.

*matched* is a single glyph that is to be moved. There needs to be a two lookups for each matched glyph.

Notice that only *lookup_basename*_matched should be added to a feature. The rest are sublookups and can be in any order. The *lookup_basename*_matched lookup is created at the point of the first move statement that has a first parameter of *lookup_basename*.

#### Examples

While there are no known use cases for this in our fonts at the moment, this is an important statement in terms of showing how complex concepts of wider interest can be implemented as extensions to fea.

##### Myanmar

Moving prevowels to the front of a syllable from their specified position in the sequence, in a DFLT processor is one such use of a move semantic:

```
move(pv, @cons, my-e);
move(pv, @cons @medial, my-e);
move(pv, @cons @medial @medial, my-e);
move(pv, @cons @medial @medial @medial, my-e);
move(pv, @cons, my-shane);
move(pv, @cons, @medial, my-shane);
```

This becomes:

```
lookup pv_pres_my-e {
	sub @cons by my-e @cons;
} pv_pres_my-e;

lookup pv_pref_my-e {
	sub @cons by my-e @cons my-e;
} pv_pref_my-e;

lookup pv_back {
	sub @cons my-e by @cons;
	sub @medial my-e by @medial;
	sub @cons my-shane by @cons;
	sub @medial my-shane by @medial;
} pv_back;

lookup pv_match {
	sub @cons' lookup pv_pres-my-e my-e' lookup pv_back;
	sub @cons' lookup pv_pref-my-e @medial my-e' lookup pv_back;
	sub @cons' lookup pv_pref-my-e @medial @medial my-e' lookup pv_back;
	sub @cons' lookup pv_pref-my-e @medial @medial @medial my-e' lookup pv_back;
	sub @cons' lookup pv_pres-my-shane my-shane' lookup pv_back;
	sub @cons' lookup pv_pref-my-shane @medial my-shane' lookup pv_back;
} pv_match;

lookup pv_pres_my-shane {
	sub @cons by my-shane @cons;
} pv_pres_my-shane;

lookup pv_pref_my-shane {
	sub @cons by my-shane @cons my-shane;
} pv_pref_my-shane;
```

##### Khmer Split Vowels

Khmer has a system of split vowels, of which we will consider a very few:

```
lookup presplit {
	sub km-oe by km-e km-ii;
	sub km-ya by km-e km-yy km-ya.sub;
	sub km-oo by km-e km-aa;
} presplit;

move(split, @cons, km-e);
move(split, @cons @medial, km-e);
```

### ifinfo

Like all if type statements, this is a macro statement that is executed during parsing rather than post parsing. ifinfo is designed to be extensible and has a syntax of:

```
ifinfo(info_type, "regexp") { … }
```

The *info_type* specifies what information is to be tested. Valid values are:

|          |                                                                            |
| -------- | -------------------------------------------------------------------------- |
| family   | Font family name as specified before fea processing                        |
| fullname | Full name including weight and italics modifiers. Regular is not included? |

The *regexp* is a regular expression that if matches means the block following the ifinfo will be parsed and added to the AST just as if the ifinfo and block elements did not exist.

#### Examples

```
ifinfo(family, "^Charis") {
	…
}
```

### ifclass

Like all if type statements, this is a macro statement that is executed during parsing rather than post parsing. ifclass tests for whether a class exists and is not empty and has a syntax of:

```
ifclass(class_name) { … }
```

#### Examples

```
ifclass(cno_sc) {
	feature smcp {
		sub @cno_sc by @c_sc;
	} smcp;
}
```

## Functions

Functions may be used in the place of a glyph or glyph class and return a list of glyphs.

### index

Used in rules where the expansion of a rule results in a particular glyph from a class being used. Where two classes need to be synchronised, and which two classes are involved, this function specifies the rule element that drives the choice of glyph from this class. This function is motivated by the Keyman language. The parameters of index() are:

```
index(slot_index, glyphclass)
```

*slot_index* considers the rule as two sequences of slots, each slot referring to one glyph or glyphclass. The first sequence is on the left hand side of the rule and the second on the right, with the index running sequentially from one sequence to the other. Thus if a rule has 2 slots on the left hand side and 3 on the right, a *slot_index* of 5 refers to the last glyph on the right hand side. *Slot_index* values start from 1 for the first glyph on the left hand side.

What makes an index() function difficult to implement is that it requires knowledge of its context in the statement it occurs in. This is tricky to implement since it is a kind of layer violation. It doesn't matter how an index() type function is represented syntactically, the same problem applies.

### infont

This function filters the glyph class that is passed to it, and returns only those glyphs, in glyphclass order, which are actually present in the font being compiled for. For example:

```
@cons = infont([ka kha gha nga]);
```

## Capabilities

### Permit classes on both sides of GSUB type 2 (multiple)✓ and type 4 (ligature)✓ lookups  [bh]

Adobe doesn't permit compact notation using groups in 1-to-many (decomposition) rules e.g:

```
    sub @AlefPlusMark by absAlef @AlefMark ;
```

or many-to-1 (ligature) rules, e.g.:

```
    sub @ShaddaKasraMarks absShadda by @ShaddaKasraLigatures ;
```

Afaict, there isn't a reason we couldn't allow this and then expand the rule to Adobe-compliant verboseness when needed.

#### Processing

Of the four simple (i.e., non-contextual) substitution lookups, Types 2 and 4 are the only ones using the  'by' keyword that have a *sequence* of glyphs or classes on one side of the rule. The other side will, necessarily, contain a single term -- which Adobe currently requires to be a glyph.  For convenience of expression, we'll call the sides of the rule the *sequence side* and the *singleton side*.

Rules that we need to expand meet the following criteria:

*   Non-contextual substitution
*   Uses the 'by' keyword
*   Singleton side references a glyph class.

Such rules are expanded by enumerating the singleton side class and the corresponding class(es) on the sequence side and writing a set of Adobe-compliant rules to give the same result.  It is an error if the singleton and corresponding classes do not have the same number of glyphs.

#### Example

Given:

```
    @class1 = [ g1  g2 ] ;
    @class2 = [ g1a g2a ] ;
```

then

```
    sub @class1 gOther by @class2 ;
```

would be rewritten as:

```
    sub g1 gOther by g1a ;
    sub g2 gOther by g2a ;
```

#### Slot correspondence ⍻

In Type 2 (multiple) substitutions, the LHS will be the singleton case and the RHS will be the sequence. In normal use-cases exactly one slot in the RHS will be a class -- all the others will be glyphs -- in which case that class and the singleton side class correspond.

If more than one RHS slot is to contain a class, then the only logical meaning is that all such classes must also correspond to the singleton class in the LHS, and will be expanded (along with the singleton side class) in parallel. Thus all the classes must have the same number of elements.

In Type 4 (ligature) substitutions, the RHS will be the singleton class. In the case that the LHS (sequence side) of the rule has class references in more than one slot, we need to identify which slot corresponds to the singleton side class.  Some alternatives:

*   Pick the slot that, when the classes are flattened, has the same number of glyphs as the class on the singleton side.  It is possible that there is more than one such slot, however.
*   Add a notation to the rule. Graphite uses the $n modifier on the RHS to identify the corresponding slot (in the context), which we could adapt to FEA as:

```
  sub @class1 @class2 @class3 by @class4$2 ;
```

Alternatively, since there can be only one such slot, we could use a simpler notation by putting something like the $ in the LHS:

```
  sub @class1 @class2$ @class3 by @class4 ;
```

[This won't look right to GDL programmers, but makes does sense for OT code]

*   Extra syntactic elements at the lexical level are hard to introduce. Instead a function such as:

```
sub @class1 @class2 @class3 by index(2, @class4);
```

Would give the necessary interpretation. See the discussion of the index() function for more details.

Note that the other classes in the LHS of ligature rules do not need further processing since FEA allows such classes.

#### Nested classes ⍻

We will want to expand nested classes in a way (i.e., depth or breadth first) that is compatible with Adobe.  **Concern:** Might this be different than Graphite? Is there any difference if one says always expand left to right? [a b [c [d e] f] g] flattens the same as [[[a b] c d] e f g] or whatever. The FontTools parser does not support nested glyph classes. To what extent are they required?