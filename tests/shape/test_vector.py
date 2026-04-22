


# def test_vector_roundtrip():
#     v = Vector(1.0, 2.0, 3.0)

#     s = BlockWriter.to_string(
#         lambda w: write_vector(w, v),
#         filetype="s",
#         fileversion="0",
#     )

#     reader = BlockReader.from_string(s)
#     v2 = read_vector(reader)

#     assert v == v2


# def test_read_vector():
#     reader = reader_from_body("""
#         vector (
#             1
#             2
#             3
#         )
#         """)
    
#     v = read_vector(reader)

#     assert v.x == 1.0
#     assert v.y == 2.0
#     assert v.z == 3.0