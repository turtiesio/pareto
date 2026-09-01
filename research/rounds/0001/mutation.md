# Mutation attacks

Scheduled mutations:

1. key captures by payload hash and thereby drop multiplicity;
2. normalize JSON and discard source octets;
3. treat absent and zero-length acquisition artifacts as equal;
4. overwrite an occurrence with the same address;
5. accept stored bytes whose declared digest no longer matches;
6. silently accept an unknown transcript-format field as if understood;
7. label uninterpreted payload “valid” merely because it was stored;
8. interpret archive append order as physical event time.

A mutation is caught only if a test or explicit unsupported/unknown result exposes it. Mutation 8 is expected to require a specification statement because no temporal evaluator exists yet.

