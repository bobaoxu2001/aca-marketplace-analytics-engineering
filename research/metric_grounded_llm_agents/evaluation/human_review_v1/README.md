# System-Label-Blinded Human Review Packet

Give each reviewer only `human_review_packet.csv`; keep
`human_review_key.json` hidden until both reviewers finish.

This is not a fully condition-blinded design: SQL, abstentions, and evidence
format may allow a reviewer to infer the system family. Randomized item IDs and
the hidden key prevent direct system labels from being shown.

Rate every item independently:

- Metric correctness: whether the operationalized metric and grain answer the question.
- Answer faithfulness: whether the answer is entailed by the displayed evidence rows.
- Caveat quality: whether material limitations or uncertainty are handled appropriately.
- Abstention: whether refusing to answer is appropriate given the supplied evidence.
- Unsupported claim: mark yes when any substantive claim lacks displayed support.

Use 1 for clearly incorrect/poor and 5 for clearly correct/strong. Review the
displayed item without attempting to identify its system. After both reviews,
join on `review_item_id`, calculate agreement,
and adjudicate disagreements before revealing the key.
