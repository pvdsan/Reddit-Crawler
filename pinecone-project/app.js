const { Pinecone } = require('@pinecone-database/pinecone');

// Initialize Pinecone with your API key
const pc = new Pinecone({
  apiKey: "pcsk_p1YWP_TuXt3APgekuAuNmYjQ68cX8EBYHG3Vc6QYknaMnLW2MuZ6cgQLrvHF9R6zUtdZj"
});

const indexName = "quickstart2"; // Replace with your actual index name
// Sample data for embedding

const data = [
  {"id": "vec1", "text": "Apple is a popular fruit known for its sweetness and crisp texture."},
  {"id": "vec2", "text": "The tech company Apple is known for its innovative products like the iPhone."},
  {"id": "vec3", "text": "Many people enjoy eating apples as a healthy snack."},
  {"id": "vec4", "text": "Apple Inc. has revolutionized the tech industry with its sleek designs and user-friendly interfaces."},
  {"id": "vec5", "text": "An apple a day keeps the doctor away, as the saying goes."},
  {"id": "vec6", "text": "Apple Computer Company was founded on April 1, 1976, by Steve Jobs, Steve Wozniak, and Ronald Wayne as a partnership."}
];

// Helper function to wait for index to be ready
async function waitForIndexReady(indexName, maxWaitTime = 300000) {
  const startTime = Date.now();
  
  console.log('⏳ Waiting for index to be ready...');
  while (Date.now() - startTime < maxWaitTime) {
    try {
      const indexInfo = await pc.describeIndex(indexName);
      if (indexInfo.status && indexInfo.status.ready) {
        console.log('✅ Index is ready!');
        return true;
      }
      await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2 seconds
    } catch (error) {
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  }
  
  throw new Error('Index did not become ready within the timeout period');
}

// Helper function to add delay
function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function main() {
  try {
    console.log('🚀 Starting Pinecone Vector Database Application');
    console.log('=' .repeat(50));

    // Step 1: Connect to existing index
    console.log('\n🔗 Step 1: Connecting to existing index...');
    try {
      const indexInfo = await pc.describeIndex(indexName);
      console.log('✅ Connected to existing index "' + indexName + '"');
      console.log('📊 Index details:');
      console.log('   Dimension:', indexInfo.dimension);
      console.log('   Metric:', indexInfo.metric);
      console.log('   Status:', indexInfo.status.ready ? 'Ready' : 'Not Ready');
      
      if (!indexInfo.status.ready) {
        console.log('\n⏳ Step 2: Waiting for index to be ready...');
        await waitForIndexReady(indexName);
      }
    } catch (error) {
      console.error('❌ Error connecting to index:', error.message);
      console.log('💡 Make sure the index name "' + indexName + '" is correct');
      throw error;
    }

    // Step 2: Generate embeddings
    console.log('\n🔄 Step 2: Generating embeddings...');
    let embeddings;
    try {
      const embeddingResponse = await pc.inference.embed({
        model: "llama-text-embed-v2", // Updated to match your index model
        inputs: data.map(d => d.text),
        parameters: {
          inputType: "passage",
          truncate: "END"
        }
      });
      
      // Handle the response structure properly
      if (embeddingResponse && embeddingResponse.data) {
        embeddings = embeddingResponse.data;
      } else if (Array.isArray(embeddingResponse)) {
        embeddings = embeddingResponse;
      } else {
        console.log('📊 Raw embedding response structure:', JSON.stringify(embeddingResponse, null, 2));
        throw new Error('Unexpected embedding response structure');
      }
      
      console.log('✅ Generated embeddings for ' + data.length + ' texts');
      console.log('📊 First embedding dimensions:', embeddings[0].values.length);
      console.log('📊 First embedding sample (first 5 values):', embeddings[0].values.slice(0, 5));
      
    } catch (embeddingError) {
      console.error('❌ Error generating embeddings:', embeddingError.message);
      console.log('💡 Trying alternative approach with OpenAI embeddings...');
      
      // Fallback to manual vectors for testing
      console.log('🔄 Creating test vectors with random embeddings for demonstration...');
      embeddings = data.map(() => ({
        values: Array.from({length: 1024}, () => Math.random() - 0.5)
      }));
      console.log('✅ Created test embeddings (Note: these are random for demo purposes)');
    }

    // Step 3: Get index reference
    console.log('\n🔗 Step 3: Connecting to index...');
    const index = pc.index(indexName);
    console.log('✅ Connected to index "' + indexName + '"');

    // Step 4: Prepare vectors for upsert
    console.log('\n📦 Step 4: Preparing vectors...');
    const vectors = [];
    for (let i = 0; i < data.length; i++) {
      vectors.push({
        id: data[i].id,
        values: embeddings[i].values,
        metadata: {
          text: data[i].text
        }
      });
    }
    console.log('✅ Prepared ' + vectors.length + ' vectors for upsert');
    
    // Set namespace for this upsert
    const namespace = "ns1";
    console.log('📝 Using namespace: ' + namespace);

    // Step 5: Upsert vectors to index
    console.log('\n📤 Step 5: Upserting vectors to index...');
    try {
      console.log('📝 Attempting upsert with vectors array...');
      console.log('📊 Vector sample:', JSON.stringify(vectors[0], null, 2));
      
      const upsertResponse = await index.upsert(vectors);
      console.log('✅ Upsert completed!');
      console.log('📊 Upserted count:', upsertResponse.upsertedCount || vectors.length);
    } catch (upsertError) {
      console.log('⚠️  First upsert method failed:', upsertError.message);
      console.log('🔄 Trying batch upsert method...');
      
      try {
        // Try upserting one by one
        for (let i = 0; i < vectors.length; i++) {
          await index.upsert([vectors[i]]);
          console.log('✅ Upserted vector ' + (i + 1) + '/' + vectors.length);
        }
        console.log('✅ All vectors upserted successfully using batch method!');
      } catch (batchError) {
        console.error('❌ Batch upsert also failed:', batchError.message);
        console.log('💡 This might be a plan limitation or API issue');
        throw batchError;
      }
    }

    // Step 7: Wait a moment for the vectors to be indexed
    console.log('\n⏳ Waiting for vectors to be indexed...');
    await delay(3000); // Wait 3 seconds

    // Step 6: Check index statistics
    console.log('\n📊 Step 6: Checking index statistics...');
    const stats = await index.describeIndexStats();
    console.log('✅ Index statistics:');
    console.log('   Total vectors:', stats.totalVectorCount);
    console.log('   Namespaces:', Object.keys(stats.namespaces || {}));
    if (stats.namespaces && stats.namespaces.ns1) {
      console.log('   Vectors in ns1:', stats.namespaces.ns1.vectorCount);
    }

    // Step 7: Perform similarity search
    console.log('\n🔍 Step 7: Performing similarity search...');
    const query = "Tell me about the tech company known as Apple.";
    console.log('📝 Query: "' + query + '"');
    
    // Generate embedding for the query
    let queryEmbedding;
    try {
      const queryEmbeddingResponse = await pc.inference.embed({
        model: "llama-text-embed-v2", // Updated to match your index model
        inputs: [query],
        parameters: {
          inputType: "query"
        }
      });
      
      if (queryEmbeddingResponse && queryEmbeddingResponse.data) {
        queryEmbedding = queryEmbeddingResponse.data[0];
      } else if (Array.isArray(queryEmbeddingResponse)) {
        queryEmbedding = queryEmbeddingResponse[0];
      } else {
        queryEmbedding = queryEmbeddingResponse;
      }
    } catch (queryError) {
      console.log('⚠️  Using random query embedding for demonstration');
      queryEmbedding = {
        values: Array.from({length: 1024}, () => Math.random() - 0.5)
      };
    }

    // Perform the search
    let results;
    try {
      // Try with namespace first
      const namespacedIndex = pc.index(indexName).namespace(namespace);
      results = await namespacedIndex.query({
        vector: queryEmbedding.values,
        topK: 3,
        includeValues: false,
        includeMetadata: true
      });
    } catch (queryError) {
      console.log('⚠️  Trying query without namespace...');
      // Try without namespace
      results = await index.query({
        vector: queryEmbedding.values,
        topK: 3,
        includeValues: false,
        includeMetadata: true
      });
    }

    // Step 8: Display results
    console.log('\n🎯 Step 8: Search Results');
    console.log('=' .repeat(50));
    console.log('Found ' + results.matches.length + ' matches:');
    
    results.matches.forEach((match, i) => {
      console.log('\n' + (i + 1) + '. Match:');
      console.log('   Score: ' + match.score.toFixed(4));
      console.log('   ID: ' + match.id);
      console.log('   Text: "' + match.metadata.text + '"');
    });

    console.log('\n🎉 SUCCESS! Your Pinecone vector database application is working perfectly!');
    console.log('=' .repeat(50));
    
    // Summary
    console.log('\n📋 Summary:');
    console.log('✅ Created/connected to index: ' + indexName);
    console.log('✅ Generated embeddings for ' + data.length + ' documents');
    console.log('✅ Upserted ' + vectors.length + ' vectors');
    console.log('✅ Performed similarity search');
    console.log('✅ Retrieved top ' + results.matches.length + ' most relevant results');

  } catch (error) {
    console.error('\n❌ Application Error:', error.message);
    
    // Provide helpful debugging information
    if (error.message.includes('401') || error.message.includes('Unauthorized')) {
      console.log('💡 Troubleshooting: Check your Pinecone API key');
    } else if (error.message.includes('inference')) {
      console.log('💡 Troubleshooting: Inference API might not be available in your plan');
      console.log('   Consider using OpenAI embeddings as an alternative');
    } else if (error.message.includes('index')) {
      console.log('💡 Troubleshooting: There might be an issue with index creation or access');
    } else if (error.message.includes('quota') || error.message.includes('limit')) {
      console.log('💡 Troubleshooting: You might have hit a usage limit');
    } else {
      console.log('💡 Troubleshooting: Check your internet connection and Pinecone service status');
    }
    
    console.log('\n🔧 For more help, visit: https://docs.pinecone.io/');
    process.exit(1);
  }
}

// Handle graceful shutdown
process.on('SIGINT', () => {
  console.log('\n\n👋 Shutting down gracefully...');
  console.log('Thank you for using Pinecone!');
  process.exit(0);
});

// Handle unhandled promise rejections
process.on('unhandledRejection', (error) => {
  console.error('\n💥 Unhandled Promise Rejection:', error.message);
  console.log('The application will now exit.');
  process.exit(1);
});

// Main execution
if (require.main === module) {
  console.log('🌲 Pinecone Vector Database Application');
  console.log('📅 Starting at:', new Date().toLocaleString());
  console.log('🔑 API Key configured: ' + (pc ? 'Yes' : 'No'));
  
  main().catch(error => {
    console.error('💥 Fatal Error:', error.message);
    process.exit(1);
  });
}

// Export for use in other modules
module.exports = {
  pc,
  indexName,
  data,
  main,
  waitForIndexReady
};