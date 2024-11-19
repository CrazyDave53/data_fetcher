# Data aggregation exercise
## The problem
Aggregating data from multiple sources to form a single data set. The data sources have different formats and structures.
## Considerations
- Flexibility: The solution should be flexible enough to handle different data sources and formats. 
- Scalability: The solution should be able to handle more data sources without significant changes.
- Maintainability: The solution should be easy to maintain and extend.

I have chosen to build a solution that can:
- Load the output json skeleton from a file and then load the data from the different sources. Each source will have a mapping file that will map the data to the output json skeleton. This way, we can easily add more data sources without changing the code just by editing the mapping file and the configuration file.
- Work with different skeleton structures and data sources by defining the skeleton and mapping files.
- Define the aggregating strategy for each field in the skeleton. This way, we can easily change the aggregation strategy for a field without changing the code.
- We can also add/edit aggregating strategies easily by just adding a new strategy class without modifying the existing code.

## Aggregating strategies

I have defined some simple aggregating strategies:
- **ModeValueStrategy:** Get the most frequent value in the data.
- **LongestValueStrategy:** Get the longest value in the data, useful for string-based data.
- **RangeValueStrategy:** Get the range of the values in the data, useful for numerical data.
- **ConcatenateValueStrategy:** Concatenate the values in the data, useful for string-based data.
- **RemoveDuplicatesStrategy:** Remove the duplicates from the data, useful for categorical/nominal data.
- **CombineValueStrategy:** Combine the values in the data, useful for combining multiple lists.
- **RemoveInvalidImageStrategy:** Remove the invalid images from the data, useful for image data.

## Extending the solution

My solution now is not perfect, and there are many ways to extend it. Here are some ideas:
- Adding more aggregation strategies. AI/ML/DS experts can help in defining more complex strategies. For example, aggregating the hotel description by using some fancy NLP techniques.
- Improving the performance of the solution. We can use parallel processing to load the data from different sources or use more efficient data structures/algorithms.
- I have done a lot of trade-offs in the solution. For example, I have chosen to aggregate the data in the HotelData class. I have traded the separation of concerns for simplicity and also for the fact that if the HotelData have its own aggregation strategies, it will be easier to add more data sources since we don't have to process from the beginning.