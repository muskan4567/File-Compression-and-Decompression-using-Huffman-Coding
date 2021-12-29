#OS module in Python provides functions for interacting with the operating system.
# OS comes under Python’s standard utility modules.
# This module provides a portable way of using operating system dependent functionality.
import heapq, os

# HUFFMAN TREE CLASS FOR FORMING HEAP AND HUFFMAN TREE
#self represents the instance of the class.
# By using the “self” keyword we can access the attributes and methods of the class in python.
# It binds the attributes with the given arguments.
#The reason you need to use self.is because Python does not use the @ syntax to refer to instance attributes.
# Python decided to do methods in a way that makes the instance to which the method belongs be
# passed automatically, but not received automatically:
# the first parameter of methods is the instance the method is called on.
class HuffmanTree:
    def __init__(self, value, frequ): #CONSTRUCTOR
        self.value = value
        self.frequ = frequ
        self.left = None
        self.right = None

    def __lt__(self, other):  #SPECIAL METHOD DESCRIBING HOW A CERTAIN OBJECT OF A CLASS SHOULD BE ARRANGED
        return self.frequ < other.frequ

    def __eq__(self, other): #SPECIAL METHOD DESCRIBING HOW A CERTAIN OBJECT OF A CLASS SHOULD BE ARRANGED
        return self.frequ == other.frequ


#HUFFMANCode CLASS FOR IMPLEMENTATION OF ALL THE FUNCTIONS NEEDED FOR COMPRESSION AND DECOMPRESSION OF FILE
class HuffmanCode:
    def __init__(self, path):
        self.path = path
        self.__heap = []  #LIST
        self.__code = {}   #DICTIONARY
        self.__reversecode = {}  #DICTIONARY

    def _frequecy_from_text(self, text): #FUNCTION FOR CALCULATING FREQUENCY OF EACH CHARACTER OF THE FILE
        freq_dict = {}; #DICTIONARY FOR STORING CHARACTER-FREQUENCY PAIR
        for char in text:
            if char not in freq_dict:
                freq_dict[char] = 1
            freq_dict[char] += 1
        return freq_dict

    def __Build_heap(self, frequency_dict): #CONSTRUCTING MIN-HEAP WITH THE HELP OF FREQ_DICT DICTIONARY
        for key in frequency_dict:
            frequency = frequency_dict[key]
            huffman_tree_node = HuffmanTree(key, frequency)
            heapq.heappush(self.__heap, huffman_tree_node)

    def __Build_huffman_tree(self):  #CONSTRUCTING HUFFMAN-TREE WITH THE HELP OF MIN-HEAP
        while len(self.__heap) > 1:
            huffman_tree_node_1 = heapq.heappop(self.__heap)
            huffman_tree_node2 = heapq.heappop(self.__heap)
            sum_of_freq = huffman_tree_node_1.frequ + huffman_tree_node2.frequ
            newnode = HuffmanTree(None, sum_of_freq)
            newnode.left = huffman_tree_node_1
            newnode.right = huffman_tree_node2
            heapq.heappush(self.__heap, newnode)

        return

    def __Build_Tree_code_Helper(self, root, curr_bits): #STORING BINARY FORM OF EACH CHARACTER
        if root is None:
            return
        if root.value is not None:
            self.__code[root.value] = curr_bits   #THIS WILL HELP AT THE TIME OF COMPRESSING FILE
            self.__reversecode[curr_bits] = root.value #THIS WILL HELP AT THE TIME OF DECOMPRESSING FILE
            return

        self.__Build_Tree_code_Helper(root.left, curr_bits + '0')
        self.__Build_Tree_code_Helper(root.right, curr_bits + '1')

    def __Build_tree_code(self):
        root = heapq.heappop(self.__heap)
        self.__Build_Tree_code_Helper(root, '')

    def __Build_Encoded_text(self, text): #CONVERTING THE ENTIRE FILE INTO BINARY BITS(ENCODED TEXT)
        encoded_text: str = ''
        char: object
        for char in text:
            encoded_text = encoded_text + self.__code[char]
        return encoded_text

    def __Build_Padded_text(self, encoded_text): #CONSTRUCTING PADDED TEXT
        padding_value = 8 - len(encoded_text) % 8
        for j in range(padding_value):
            encoded_text += '0'

        padded_info = "{0:08b}".format(padding_value) #THIS WILL CONVERT THE PADDING_VALUE INTO 8-BIT BINARY
        padded_text = padded_info + encoded_text #ADDING PADDED_INFO AT BEGINNING FOR KNOWING HOW MANY BITS
        #WE HAVE ADDED AT THE END FOR FORMING PAIR OF 8-BITS BINARY DIGIT
        return padded_text

    def __Build_byte_array(self, padded_text): #CONVERTING PADDED_TEXT INTO INTEGER FORMAT
        array = []
        i: int
        for i in range(0, len(padded_text), 8):
            byte = padded_text[i:i + 8] #TAKING 8-BITS BINARY DIGIT AND CONVERTING INTO INTEGER
            array.append(int(byte, 2))  #STORING THE INTEGERS IN ARRAY

        return array


#The open() function opens a file in text format by default.
#To open a file in binary format, add 'b' to the mode parameter.
# Hence the "rb" mode opens the file in binary format for reading,
# while the "wb" mode opens the file in binary format for writing.
# Unlike text files, binary files are not human-readable.
#r+ : Opens a file for reading and writing, placing the pointer at the beginning of the file.
# w : Opens in write-only mode.
# The pointer is placed at the beginning of the file and this will overwrite any existing file
# with the same name. It will create a new file if one with the same name doesn't exist.
    def compression(self):
        print('Compression of file starts')
        #os.path.splitext() method in Python is used to split the path name into a pair root and ext.
        # Here, ext stands for extension and has the extension portion of the specified path while
        # root is everything except ext part.
        filename, file_extension = os.path.splitext(self.path)
        output_path = filename + '.bin'
        with open(self.path, 'r+') as file, open(output_path, 'wb') as output:
            text = file.read()
            #rstrip() method returns a copy of the string with trailing(from last) characters removed
            # (based on the string argument passed). If no argument is passed, it removes trailing spaces.
            text = text.rstrip()
            frequency_dict = self._frequecy_from_text(text)
            self.__Build_heap(frequency_dict)
            self.__Build_huffman_tree()
            self.__Build_tree_code()
            encoded_text = self.__Build_Encoded_text(text)
            padded_text = self.__Build_Padded_text(encoded_text)
            bytes_array = self.__Build_byte_array(padded_text)
            final_bytes = bytes(bytes_array)
            output.write(final_bytes)
            print('compressed successfully')
        return output_path

    def __Remove_Padding(self, bit_string):
        padded_info = bit_string[:8]
        padding_value = int(padded_info, 2)
        bit_string = bit_string[8:]
        bit_string = bit_string[: -1 * padding_value]
        return bit_string

    def __Decoded_text(self, text):
        current_bits = ''
        decoded_text = ''
        for char in text:
            current_bits += char
            if current_bits in self.__reversecode:
                decoded_text += self.__reversecode[current_bits]
                current_bits = ''

        return decoded_text

    def decompress(self, input_path):
        print('decompression starts')
        filename, file_extension = os.path.splitext(input_path)
        output_path = filename + '_decompressed' + '.txt'
        with open(input_path, 'rb') as file, open(output_path, 'w') as output:
            bit_string = ''
            byte = file.read(1)
            while byte:
                byte = ord(byte) #ord returns the Unicode code from a given character.
                bits = bin(byte)[2:].rjust(8, '0') #convert that integer into 8-bit binary format
                bit_string += bits
                byte = file.read(1)

            remove_padding = self.__Remove_Padding(bit_string) #Removal of padding
            actual_text = self.__Decoded_text(remove_padding)  #Building actual text from self.__Reversecode
            output.write(actual_text)
            print('decompressed successfully')
        return output_path


path = input("Enter the path of your file which you need to compress")
h = HuffmanCode(path)
compressed_file = h.compression()
h.decompress(compressed_file)